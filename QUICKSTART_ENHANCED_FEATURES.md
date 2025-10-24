# 🚀 Quick Start - Enhanced ROI & Line Editor

## ⚡ 5-Minute Setup Guide

---

## 🎯 Queue Monitor - Draw Areas in 30 Seconds

### Steps:
1. **Dashboard** → Queue Monitor → **"Edit ROI"**
2. **Click 4 points** on video for queue area (Yellow appears)
3. **Switches automatically** to counter mode
4. **Click 4 points** for counter area (Cyan appears)
5. **Drag any point** if needed to adjust
6. **Click "Save ROI"** ✅

### Visual:
```
┌──────────────────────────┐
│ Video Feed               │
│                          │
│  ╔═══════╗ ← Queue (Y)   │
│  ║ 1   2 ║               │
│  ║ 4   3 ║               │
│  ╚═══════╝               │
│                          │
│  ┌───┐ ← Counter (C)     │
│  │1 2│                   │
│  │4 3│                   │
│  └───┘                   │
└──────────────────────────┘
```

---

## 📏 People Counter - Set Line in 20 Seconds

### Steps:
1. **Dashboard** → People Counter → **"Edit Counting Line"**
2. **Choose orientation:** Vertical / Horizontal / Free
3. **Drag line** to desired position
4. **Verify labels:** "IN →" and "← OUT"
5. **Click "Save Line"** ✅

### Visual:
```
Vertical (Default):
    OUT ←  │  → IN
           │ (Green Line)
           │

Horizontal:
    ─────────────
    ↑ OUT
    ─────────────
    IN ↓

Free Angle:
    Drag endpoints
    to any position
```

---

## 🎨 Features at a Glance

### Queue Monitor ROI:
| Feature | What It Does |
|---------|--------------|
| **4 Points** | Click 4 times to define area |
| **Auto-Close** | Polygon completes automatically |
| **Drag Points** | Reposition any point |
| **2 Areas** | Queue (Yellow) + Counter (Cyan) |
| **Reset** | Clear current or all |

### People Counter Line:
| Feature | What It Does |
|---------|--------------|
| **3 Modes** | Vertical / Horizontal / Free |
| **Drag Line** | Move entire line |
| **Drag Ends** | Adjust endpoints |
| **Labels** | Shows IN/OUT directions |
| **Save** | Persists across restarts |

---

## 🎯 Common Tasks

### Task: Define Queue Area
```
1. Click "Edit ROI"
2. Click 4 corners of queue zone
3. Done! (Auto-closes)
```

### Task: Define Counter Area
```
1. After queue, automatically switches
2. Click 4 corners of counter
3. Done! (Auto-closes)
```

### Task: Adjust Point Position
```
1. Hover over point → cursor changes to 'move'
2. Click and drag to new position
3. Release mouse → point updated
```

### Task: Change Counting Line
```
1. Click "Edit Counting Line"
2. Click "Vertical" or "Horizontal"
3. Drag line to position
4. Click "Save Line"
```

### Task: Make Angled Line
```
1. Click "Edit Counting Line"
2. Click "Free Angle"
3. Drag each endpoint to desired position
4. Click "Save Line"
```

---

## 🔧 Controls Reference

### Queue Monitor Buttons:
| Button | Action |
|--------|--------|
| **Edit ROI** | Open editor |
| **Draw Queue** | Switch to queue area |
| **Draw Counter** | Switch to counter area |
| **Reset Current** | Clear active area only |
| **Clear All** | Remove all points |
| **Cancel** | Exit without saving |
| **Save ROI** | Save configuration |

### People Counter Buttons:
| Button | Action |
|--------|--------|
| **Edit Counting Line** | Open editor |
| **Vertical** | Set vertical line |
| **Horizontal** | Set horizontal line |
| **Free Angle** | Custom angle |
| **Cancel** | Exit without saving |
| **Save Line** | Save configuration |

---

## 💡 Pro Tips

### Queue ROI:
✅ **Draw during quiet hours** for better visibility  
✅ **Test with actual people** to verify coverage  
✅ **Avoid overlapping** queue and counter areas  
✅ **Rectangular shapes** work best  
✅ **4 points minimum** required for each area

### Counting Line:
✅ **Perpendicular to flow** for best accuracy  
✅ **Span entire path** to catch all crossings  
✅ **Test both directions** after saving  
✅ **Consider camera angle** when positioning  
✅ **Vertical line** best for doorways

---

## 🐛 Troubleshooting

### "Nothing happens when I click Edit ROI"
→ Refresh page and try again  
→ Check browser console (F12) for errors

### "Points don't appear"
→ Canvas might not be sized - refresh page  
→ Ensure video feed is loading

### "Can't drag points"
→ Hover directly over point circle  
→ Wait for cursor to change to 'move'

### "Line won't save"
→ Check internet connection  
→ Verify backend is running  
→ Look for error alert message

---

## 📊 Visual Feedback

### Queue ROI Colors:
- **Queue Area:** 🟨 Yellow with numbers (1,2,3,4)
- **Counter Area:** 🔵 Cyan with numbers (1,2,3,4)
- **Active Area:** Thicker lines (3px)
- **Inactive Area:** Thinner lines (2px)

### Line Editor:
- **Line:** 🟢 Green (3px thick)
- **Endpoints:** Green circles with white border
- **Labels:** White text, black outline
- **Orientation:** Changes labels automatically

---

## 🎯 Testing Your Setup

### Queue Monitor:
1. Draw ROI areas
2. Have people stand in queue area
3. Check "Queue: X" count updates
4. Have person at counter
5. Check "Counter Area: Y" updates
6. Verify alert triggers correctly

### People Counter:
1. Set counting line
2. Walk across line left-to-right
3. Check "IN" count increases
4. Walk across line right-to-left
5. Check "OUT" count increases
6. Verify both directions work

---

## 🚀 What Changed

### Before:
❌ Canvas didn't show  
❌ No visual points  
❌ Couldn't adjust after placing  
❌ No line editor  

### After:
✅ Canvas appears immediately  
✅ Numbered, visible points  
✅ Full drag-and-drop  
✅ Complete line editor  
✅ Auto-close polygons  
✅ Real-time feedback  

---

## 📚 More Help

**Detailed Guide:** `ENHANCED_ROI_GUIDE.md`  
**Technical Docs:** `IMPLEMENTATION_COMPLETE_V2.md`  
**API Reference:** `ENHANCED_ROI_GUIDE.md` (API section)  
**Original Guide:** `ROI_EDITING_GUIDE.md`

---

## ✅ Checklist

Before you start:
- [ ] Dashboard accessible
- [ ] Video feeds loading
- [ ] Backend running
- [ ] Browser supports Canvas API

After setup:
- [ ] Queue ROI saved
- [ ] Counter ROI saved
- [ ] Counting line saved
- [ ] Tested with actual people
- [ ] Verified counts updating
- [ ] Verified persistence (restart test)

---

## 🎊 You're Ready!

**Your system now has:**
✨ Enhanced Queue Monitor with draggable ROI  
✨ People Counter with editable counting line  
✨ Visual feedback and real-time updates  
✨ Database persistence  

**Access your dashboard:**
```
http://182.65.205.121:5001/dashboard
```

**Start editing:**
1. Queue Monitor → "Edit ROI"
2. People Counter → "Edit Counting Line"

---

**Quick Start Version:** 1.0  
**Last Updated:** October 24, 2025  
**Time to Setup:** < 5 minutes

🎉 **Start drawing your ROIs now!**

