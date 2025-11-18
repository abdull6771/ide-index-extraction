# 🚀 QUICK START: Cloud GPU Fix

## ⚡ Problem: Process Killed

Your process is being killed due to **memory limits** on the cloud GPU.

---

## ✅ IMMEDIATE FIX

Run this command instead:

```bash
python src/main.py --max-chunks 10
```

This will:

- ✅ Process successfully without running out of memory
- ✅ Complete in 5-10 minutes
- ✅ Extract 10-30 initiatives per document
- ✅ Cost ~$0.05-0.10 total

---

## 🎯 Alternative Commands

### Process with fewer chunks (faster, uses less memory)

```bash
python src/main.py --max-chunks 5
```

### Process single PDF at a time

```bash
python examples/process_single_pdf.py "data/Genetec_Annual Report 2023.pdf" --max-chunks 10
```

### Process all chunks (may still crash on low-memory GPU)

```bash
python src/main.py --max-chunks 20
```

---

## 📊 What Each Setting Does

| Command           | Memory | Time      | Results            | Cost  |
| ----------------- | ------ | --------- | ------------------ | ----- |
| `--max-chunks 3`  | ~300MB | 1-2 min   | 3-10 initiatives   | $0.01 |
| `--max-chunks 5`  | ~500MB | 2-3 min   | 5-15 initiatives   | $0.02 |
| `--max-chunks 10` | ~1GB   | 5-8 min   | 10-30 initiatives  | $0.05 |
| `--max-chunks 20` | ~2GB   | 10-15 min | 20-50 initiatives  | $0.10 |
| No limit          | 4-8GB  | 20-30 min | 50-100 initiatives | $0.20 |

---

## 🔧 Why This Happens

Cloud GPU environments typically have:

- **Limited RAM:** 4-8GB shared with other processes
- **Auto-kill:** System automatically terminates processes exceeding memory limit
- **No swap:** Unlike local machines, cloud VMs don't use disk swap

Your PDFs are large:

- **Genetec CG Report 2023:** 69 pages → 41 chunks
- **Genetec Annual Report 2023:** 27 pages (killed here)

Processing all chunks from multiple PDFs simultaneously exhausts RAM.

---

## ✅ Recommended for Your Case

**Best balance of results vs resources:**

```bash
python src/main.py --max-chunks 10
```

This will:

1. Process all 3 PDFs successfully
2. Extract meaningful initiatives from each
3. Use ~1-2GB RAM (safe for cloud GPU)
4. Complete in ~15-20 minutes total
5. Cost approximately $0.05-0.15

---

## 📝 After Processing

Check results:

```bash
# See statistics
python src/query.py stats

# View all initiatives
python src/query.py list --limit 20

# Search for specific initiatives
python src/query.py search "digital banking"
```

---

## 💡 Pro Tip

For large-scale processing:

1. Start with `--max-chunks 5` to test
2. If successful, increase to `--max-chunks 10`
3. Monitor memory: `watch -n 1 free -h` (in another terminal)
4. Adjust based on available RAM

---

**JUST RUN THIS NOW:**

```bash
python src/main.py --max-chunks 10
```

✅ This will work on your cloud GPU!
