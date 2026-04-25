#!/usr/bin/env python3
# diagnose.py — Inspect ChromaDB collections and storage

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import chromadb


def main():
    chroma_path = "./data/chroma_db"
    
    print("=" * 60)
    print("ChromaDB Diagnostic Report")
    print("=" * 60)
    
    # Check if path exists
    if not Path(chroma_path).exists():
        print(f"\nERROR: ChromaDB path does not exist: {chroma_path}")
        print("Run 'python ingestion.py' first to create the database.")
        return
    
    # Connect to ChromaDB
    client = chromadb.PersistentClient(path=chroma_path)
    
    # List collections
    collections = client.list_collections()
    
    print(f"\nPath: {chroma_path}")
    print(f"Collections found: {len(collections)}")
    print("-" * 60)
    
    if not collections:
        print("\nNo collections found. Run 'python ingestion.py' to create one.")
        return
    
    print("\n{:<30} {:>10}".format("Collection Name", "Items"))
    print("-" * 45)
    
    for col in collections:
        collection = client.get_collection(col.name)
        count = collection.count()
        print(f"{col.name:<30} {count:>10}")
    
    # Show physical folders
    print("\n" + "=" * 60)
    print("Physical Storage (subfolders in chroma_db)")
    print("=" * 60)
    
    folders = [d for d in Path(chroma_path).iterdir() if d.is_dir()]
    if folders:
        for folder in sorted(folders):
            files = list(folder.glob("*"))
            total_size = sum(f.stat().st_size for f in files)
            print(f"\n  {folder.name}/")
            print(f"    Total size: {total_size / 1024:.1f} KB")
            for f in files:
                size_kb = f.stat().st_size / 1024
                print(f"    {f.name} ({size_kb:.1f} KB)")
    else:
        print("\nNo subfolders found.")
    
    print("\n" + "=" * 60)
    print("Diagnostic Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()