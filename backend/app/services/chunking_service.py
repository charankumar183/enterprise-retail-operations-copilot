import re
from typing import List, Dict, Any, Tuple
from backend.app.config import settings

class ChunkItem:
    def __init__(
        self,
        chunk_id: str,
        content: str,
        is_parent: bool = False,
        parent_chunk_id: str = None,
        section_title: str = "",
        page_number: int = 1,
        metadata: Dict[str, Any] = None
    ):
        self.chunk_id = chunk_id
        self.content = content
        self.is_parent = is_parent
        self.parent_chunk_id = parent_chunk_id
        self.section_title = section_title
        self.page_number = page_number
        self.metadata = metadata or {}

class ChunkingService:
    def __init__(
        self,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
        parent_chunk_size: int = settings.PARENT_CHUNK_SIZE,
        child_chunk_size: int = settings.CHILD_CHUNK_SIZE
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.separators = ["\n\n", "\n", ". ", "; ", ", ", " "]

    def recursive_character_chunk(self, text: str, max_size: int, overlap: int) -> List[str]:
        """Recursive Character Chunking implementation."""
        text = text.strip()
        if len(text) <= max_size:
            return [text] if text else []

        chunks = []
        # Find appropriate separator
        chosen_sep = " "
        for sep in self.separators:
            if sep in text:
                chosen_sep = sep
                break

        splits = text.split(chosen_sep)
        current_chunk = ""

        for part in splits:
            candidate = f"{current_chunk}{chosen_sep}{part}" if current_chunk else part
            if len(candidate) <= max_size:
                current_chunk = candidate
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # Handle overlap: take trailing characters from current_chunk
                if overlap > 0 and len(current_chunk) > overlap:
                    overlap_prefix = current_chunk[-overlap:]
                    current_chunk = f"{overlap_prefix} {part}".strip()
                else:
                    current_chunk = part

        if current_chunk:
            chunks.append(current_chunk.strip())

        # Post-process any chunks that exceed max_size by forced windowing
        final_chunks = []
        for ch in chunks:
            if len(ch) > max_size * 1.5:
                # Force slice
                for i in range(0, len(ch), max_size - overlap):
                    sub = ch[i:i + max_size].strip()
                    if sub:
                        final_chunks.append(sub)
            else:
                final_chunks.append(ch)

        return final_chunks

    def metadata_based_chunk(
        self,
        document_text: str,
        base_metadata: Dict[str, Any]
    ) -> List[ChunkItem]:
        """
        Metadata-Based Chunking: Partitions unstructured document along semantic section,
        heading, page, and policy boundaries, enriching each chunk with metadata tags.
        """
        pattern = r'(?m)^(#{1,3}\s+[^\n]+|[A-Z\s]{4,}:|Section\s+\d+[:\s]+[^\n]+)'
        splits = re.split(pattern, document_text)
        
        chunks = []
        current_title = base_metadata.get("doc_type", "General Section")
        idx = 0
        
        if len(splits) <= 1:
            raw_splits = self.recursive_character_chunk(document_text, self.chunk_size, self.chunk_overlap)
            for s in raw_splits:
                idx += 1
                chunks.append(ChunkItem(
                    chunk_id=f"meta_chunk_{idx}",
                    content=s,
                    is_parent=False,
                    section_title=current_title,
                    metadata={**base_metadata, "chunk_index": idx, "section": current_title}
                ))
            return chunks

        for i in range(1, len(splits), 2):
            heading = splits[i].strip("# \t\r\n")
            body = splits[i+1].strip() if i+1 < len(splits) else ""
            if not body:
                continue
            
            sub_chunks = self.recursive_character_chunk(body, self.chunk_size, self.chunk_overlap)
            for sc in sub_chunks:
                idx += 1
                chunks.append(ChunkItem(
                    chunk_id=f"meta_chunk_{idx}",
                    content=f"{heading}\n{sc}",
                    is_parent=False,
                    section_title=heading[:100],
                    metadata={
                        **base_metadata,
                        "chunk_index": idx,
                        "section_title": heading[:100],
                        "doc_type": base_metadata.get("doc_type", "Store SOPs")
                    }
                ))
        return chunks

    def create_parent_child_chunks(
        self,
        doc_id: int,
        sections: List[Any],
        doc_metadata: Dict[str, Any]
    ) -> Tuple[List[ChunkItem], List[ChunkItem]]:
        """
        Creates parent chunks (larger business context) and child chunks (fine-grained vectors).
        Returns (parent_chunks, child_chunks)
        """
        parent_chunks: List[ChunkItem] = []
        child_chunks: List[ChunkItem] = []
        
        parent_idx = 0
        child_idx = 0

        for sec in sections:
            sec_title = getattr(sec, "title", "Section")
            sec_content = getattr(sec, "content", "")
            page_num = getattr(sec, "page_number", 1)
            
            if not sec_content.strip():
                continue

            # Step 1: Split section into parent chunks (large context windows, e.g. 1500 chars)
            raw_parents = self.recursive_character_chunk(sec_content, self.parent_chunk_size, 150)
            
            for p_text in raw_parents:
                parent_idx += 1
                p_id = f"doc_{doc_id}_p_{parent_idx}"
                p_item = ChunkItem(
                    chunk_id=p_id,
                    content=p_text,
                    is_parent=True,
                    parent_chunk_id=None,
                    section_title=sec_title,
                    page_number=page_num,
                    metadata={**doc_metadata, "parent_id": p_id, "is_parent": True}
                )
                parent_chunks.append(p_item)

                # Step 2: Split this parent into child chunks (e.g. 350 chars) for precise retrieval
                raw_children = self.recursive_character_chunk(p_text, self.child_chunk_size, self.chunk_overlap)
                for c_text in raw_children:
                    child_idx += 1
                    c_id = f"doc_{doc_id}_c_{child_idx}"
                    c_item = ChunkItem(
                        chunk_id=c_id,
                        content=c_text,
                        is_parent=False,
                        parent_chunk_id=p_id,
                        section_title=sec_title,
                        page_number=page_num,
                        metadata={**doc_metadata, "parent_id": p_id, "child_id": c_id, "is_parent": False}
                    )
                    child_chunks.append(c_item)

        return parent_chunks, child_chunks
