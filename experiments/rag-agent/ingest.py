from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_INDEX_PATH = BASE_DIR / "index.json"
FRONT_MATTER_BOUNDARY = "---"
SPAN_PATTERN = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]+", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for span in SPAN_PATTERN.findall(text.lower()):
        if re.fullmatch(r"[\u4e00-\u9fff]+", span):
            if len(span) == 1:
                tokens.append(span)
            else:
                tokens.extend(span[index : index + 2] for index in range(len(span) - 1))
        else:
            tokens.append(span)
    return tokens


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONT_MATTER_BOUNDARY:
        return {}, text

    metadata: dict[str, str] = {}
    end = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == FRONT_MATTER_BOUNDARY:
            end = index
            break
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    if end is None:
        raise ValueError("Front matter is missing a closing boundary")
    return metadata, "\n".join(lines[end + 1 :])


def split_sections(body: str) -> list[tuple[str, str, str]]:
    sections: list[tuple[str, str, str]] = []
    section_id = "ROOT"
    heading = "Overview"
    paragraphs: list[str] = []

    def flush() -> None:
        text = "\n".join(paragraphs).strip()
        if text:
            sections.append((section_id, heading, text))

    for raw_line in body.splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            flush()
            label = line[3:].strip()
            first, _, rest = label.partition(" ")
            section_id = first
            heading = rest or first
            paragraphs = []
        elif line.startswith("# "):
            continue
        elif line:
            paragraphs.append(line)
    flush()
    return sections


def load_chunks(data_dir: Path = DEFAULT_DATA_DIR) -> list[dict[str, object]]:
    chunks: list[dict[str, object]] = []
    for path in sorted(data_dir.rglob("*.md")):
        metadata, body = parse_front_matter(path.read_text(encoding="utf-8"))
        required = {"document_id", "title", "version", "effective_date", "status"}
        missing = required.difference(metadata)
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"{path} is missing metadata: {names}")

        source = str(path.relative_to(BASE_DIR))
        for section_id, heading, text in split_sections(body):
            searchable = f"{metadata['title']} {heading} {heading} {text}"
            tokens = tokenize(searchable)
            chunks.append(
                {
                    "id": f"{metadata['document_id']}:{section_id}",
                    "source": source,
                    "document_id": metadata["document_id"],
                    "title": metadata["title"],
                    "version": metadata["version"],
                    "effective_date": metadata["effective_date"],
                    "status": metadata["status"],
                    "section": section_id,
                    "heading": heading,
                    "text": text,
                    "tokens": tokens,
                    "length": len(tokens),
                }
            )
    return chunks


def build_index(
    data_dir: Path = DEFAULT_DATA_DIR,
    index_path: Path = DEFAULT_INDEX_PATH,
) -> dict[str, object]:
    payload: dict[str, object] = {"schema_version": 1, "chunks": load_chunks(data_dir)}
    index_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the local policy index")
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH)
    args = parser.parse_args()

    payload = build_index(args.data_dir, args.index)
    print(f"Indexed {len(payload['chunks'])} sections from {args.data_dir}")
    print(f"Wrote {args.index}")


if __name__ == "__main__":
    main()
