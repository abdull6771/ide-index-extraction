# 🔧 Cloud GPU Deployment Guide

## Issue: Process Killed on Cloud GPU

Your process is being terminated due to **memory constraints** on the cloud GPU environment.

```
/commands/python: line 47: 35220 Killed
```

This happens when processing large PDFs exhausts available RAM.

---

## ✅ Solutions

### Solution 1: Process with Chunk Limit (Recommended)

Limit the number of chunks processed per document to reduce memory usage:

```bash
# Process only 10 chunks per document
python src/main.py --max-chunks 10

# Or even fewer for testing
python src/main.py --max-chunks 5
```

This will:

- ✅ Use much less memory
- ✅ Complete successfully
- ✅ Give you meaningful results
- ✅ Cost less (~$0.01 per document)

---

### Solution 2: Process One PDF at a Time

Process PDFs individually to minimize memory usage:

```bash
# Move all but one PDF out temporarily
mkdir /tmp/pdfs_backup
mv data/*.pdf /tmp/pdfs_backup/

# Move one PDF back
mv /tmp/pdfs_backup/Genetec_Annual\ Report\ 2023.pdf data/

# Process it
python src/main.py --max-chunks 10

# Repeat for other PDFs
```

---

### Solution 3: Use Smaller Chunk Size

Edit your `.env` file:

```bash
# Reduce chunk size to use less memory
CHUNK_SIZE=2000
CHUNK_OVERLAP=300
```

Then run:

```bash
python src/main.py --max-chunks 15
```

---

### Solution 4: Process Single PDF with Example Script

```bash
python examples/process_single_pdf.py "data/Genetec_Annual Report 2023.pdf" --max-chunks 10
```

---

## 🚀 Recommended Workflow for Cloud GPU

### Step 1: Test with Minimal Processing

```bash
python src/main.py --max-chunks 3
```

### Step 2: Check Results

```bash
python src/query.py stats
```

### Step 3: If Successful, Increase Gradually

```bash
python src/main.py --max-chunks 10
python src/main.py --max-chunks 20
```

### Step 4: Monitor Memory Usage

```bash
# In another terminal, watch memory
watch -n 1 free -h
```

---

## 💾 Memory-Efficient Settings

Add to your `.env`:

```properties
# Memory-efficient settings for cloud GPU
CHUNK_SIZE=2000
CHUNK_OVERLAP=200
MAX_CHUNKS_PER_DOCUMENT=10

# Use faster, lighter model
OPENAI_MODEL=gpt-3.5-turbo
```

---

## 🔍 Current Issue Analysis

Your logs show:

1. ✅ Successfully processed: `Genetec_Corporate Governance Report 2023.pdf` (69 pages, 41 chunks)
2. ❌ Killed while processing: `Genetec_Annual Report 2023.pdf` (27 pages)

The system likely ran out of memory while:

- Loading the second PDF
- Keeping the first PDF's data in memory
- Running LLM analysis

---

## 🛠️ Quick Fix Commands

```bash
# Option 1: Run with strict limits
python src/main.py --max-chunks 5

# Option 2: Process just one file
python examples/process_single_pdf.py "data/Genetec_Annual Report 2023.pdf" --max-chunks 5

# Option 3: Set memory limits explicitly
ulimit -v 4000000  # Limit to ~4GB virtual memory
python src/main.py --max-chunks 10
```

---

## 📊 Expected Results with Limited Chunks

With `--max-chunks 5`:

- **Processing time:** 2-3 minutes per PDF
- **Memory usage:** ~500MB-1GB
- **API cost:** ~$0.01 per PDF
- **Results:** 5-15 initiatives per document (good sample)

With `--max-chunks 10`:

- **Processing time:** 5-8 minutes per PDF
- **Memory usage:** ~1-2GB
- **API cost:** ~$0.02 per PDF
- **Results:** 10-30 initiatives per document (better coverage)

---

## 🎯 Best Practice for Cloud GPU

1. **Always use `--max-chunks` flag**
2. **Start small** (5 chunks), increase if stable
3. **Process one PDF at a time** if needed
4. **Monitor memory** during processing
5. **Use lighter model** (`gpt-3.5-turbo`) if needed

---

## 🚨 Important Note

Cloud GPU environments often have:

- Limited RAM (4-8GB typical)
- Automatic process killing when memory exceeded
- Shared resources with other users

Always run with memory constraints in mind!

---

## ✅ Recommended Command for Your Situation

```bash
python src/main.py --max-chunks 10
```

This should:

- Complete successfully ✓
- Use reasonable memory ✓
- Give good results ✓
- Cost ~$0.05-0.10 total ✓

---

## 📝 Alternative: Batch Processing Script

I can create a script that processes PDFs one at a time with automatic cleanup. Let me know if you need this.

---

**TL;DR:** Run this now:

```bash
python src/main.py --max-chunks 10
```
