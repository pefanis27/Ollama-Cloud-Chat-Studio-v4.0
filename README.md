# ☁️ Ollama Cloud Chat Studio v6.0 (update)

Ένα browser-based studio συνομιλίας για **Ollama Cloud** με ενσωματωμένο HTTP server, streaming απαντήσεις, υποστήριξη αρχείων, prompt profiles, visualization engine, dual-model ensemble και εξαγωγή απαντήσεων σε **Markdown, PDF και Docx**.

![unnamed](unnamed.png)


---

## Περιεχόμενα

- [Τι είναι η εφαρμογή](#τι-είναι-η-εφαρμογή)
- [Βασικές δυνατότητες](#βασικές-δυνατότητες)
- [Προαπαιτούμενα](#προαπαιτούμενα)
- [Εγκατάσταση](#εγκατάσταση)
- [Εκτέλεση](#εκτέλεση)
- [Πρώτη ρύθμιση](#πρώτη-ρύθμιση)
- [Αναλυτικός οδηγός χρήσης](#αναλυτικός-οδηγός-χρήσης)
- [Αρχεία και αποθηκεύσεις της εφαρμογής](#αρχεία-και-αποθηκεύσεις-της-εφαρμογής)
- [Εξαγωγές και generated artifacts](#εξαγωγές-και-generated-artifacts)
- [Παράμετροι εκκίνησης από γραμμή εντολών](#παράμετροι-εκκίνησης-από-γραμμή-εντολών)
- [Troubleshooting](#troubleshooting)
- [Χρήσιμες πρακτικές](#χρήσιμες-πρακτικές)
- [Περιορισμοί](#περιορισμοί)

---

## Τι είναι η εφαρμογή

Το **Ollama Cloud Chat Studio v6.0** είναι μια τοπικά εκτελούμενη εφαρμογή Python που ανοίγει ένα σύγχρονο web UI στον browser και επιτρέπει συνομιλία με **official Ollama Cloud models** μέσω direct cloud API.

Η εφαρμογή συνδυάζει:

- ανακάλυψη και ευρετική ταξινόμηση μοντέλων,
- streaming απαντήσεις,
- υποστήριξη μαθηματικών, scientific formatting, Markdown και SVG,
- διαχείριση συνημμένων,
- προσαρμογή system prompt,
- έξυπνες οπτικοποιήσεις,
- export απαντήσεων,
- και βοηθητικές λειτουργίες για Python code blocks.

Σχεδιάστηκε ώστε να είναι ιδιαίτερα χρήσιμη για:

- τεχνική συγγραφή,
- προγραμματισμό,
- debugging,
- μαθηματικά και φυσική,
- εκπαιδευτικό υλικό,
- διαγράμματα,
- και παραγωγή τεκμηρίωσης έτοιμης για αποθήκευση ή εξαγωγή.

---

## Βασικές δυνατότητες

### 1. Direct Ollama Cloud API
Η εφαρμογή λειτουργεί σε **direct Ollama Cloud API mode**. Δεν στηρίζεται σε τοπικό Ollama daemon για τη βασική λειτουργία συνομιλίας.

### 2. Model discovery και model ranking
Ανακτά τη λίστα των διαθέσιμων cloud models και τα ταξινομεί ευρετικά με βάση:

- overall ποιότητα,
- coding,
- reasoning,
- long context,
- vision,
- speed,
- freshness / νεότητα μοντέλου.

### 3. Thinking Mode
Υποστηρίζει πολλαπλά thinking / reasoning modes:

- `Auto`
- `On`
- `Off`
- `Low`
- `Medium`
- `High`

Η εφαρμογή κάνει και compatibility fallback όταν ένα μοντέλο δεν υποστηρίζει ακριβώς το ζητούμενο think profile.

### 4. Dual Model Ensemble
Υποστηρίζεται λειτουργία δύο μοντέλων:

- **Off**: μόνο το κύριο μοντέλο
- **Auto**: αυτόματη επιλογή helper model
- **Manual**: χειροκίνητη επιλογή δεύτερου μοντέλου

Αυτό είναι χρήσιμο όταν θέλετε δεύτερο μοντέλο για:

- vision βοήθεια,
- code review,
- extra reasoning,
- cross-check,
- long-context assistance.

### 5. Prompt Profiles
Περιλαμβάνονται ενσωματωμένα prompt profiles για διαφορετικά σενάρια χρήσης:

- Scientific / Technical Expert
- Code Development / Production Engineering
- Educational / Teacher Mode
- Math & Physics Solver
- Code Reviewer / Debugger
- Research / Structured Analysis
- Diagram & Visualization Mode
- Concise Engineer

### 6. Visualization Engine
Μπορείτε να καθορίσετε πώς θα παραχθούν οπτικοποιήσεις:

- **Auto**
- **SVG / Diagrams**
- **Python Plot / matplotlib**

Το studio δίνει προτεραιότητα σε SVG για εννοιολογικά / θεωρητικά διαγράμματα και σε matplotlib για πραγματικά υπολογιστικά plots.

### 7. Συνημμένα αρχεία και drag & drop
Υποστηρίζονται:

- εικόνες,
- κείμενα,
- αρχεία κώδικα,
- Markdown,
- JSON,
- CSV,
- PDF,
- και πολλά ακόμη αρχεία text-based context.

Οι εικόνες μπορούν να σταλούν natively σε vision-capable models, ενώ τα υπόλοιπα αρχεία γίνονται excerpt/context injection όπου υποστηρίζεται.

### 8. Εξαγωγές
Η εφαρμογή υποστηρίζει:

- εξαγωγή συνομιλίας σε `.md`,
- εξαγωγή απάντησης assistant σε **PDF**,
- εξαγωγή απάντησης assistant σε **Docx**.

### 9. Python code block utilities
Όταν η απάντηση περιέχει Python code block, η εφαρμογή μπορεί να:

- το αποθηκεύσει ως `.py`,
- να επιχειρήσει εκτέλεση σε νέο terminal,
- και να κάνει ασφαλές render matplotlib plot σε generated media αρχείο.

---

## Προαπαιτούμενα

### Υποχρεωτικά

- Εγκατεστημένη **Python**
- Έγκυρο **Ollama Cloud API key**
- Σύνδεση στο διαδίκτυο για cloud chat και online model refresh

### Προτεινόμενα Python πακέτα

```bash
pip install beautifulsoup4 python-docx pillow pygments pypdf cairosvg pymupdf
```

### Σημειώσεις για dependencies

- `beautifulsoup4`: HTML parsing / μετασχηματισμοί
- `python-docx`: δημιουργία αρχείων Docx
- `Pillow`: image normalization για exports
- `pygments`: syntax-aware χρωματισμός / fallback runs
- `pypdf`: fallback PDF polish
- `cairosvg`: χρήσιμο όταν χρειάζεται μετατροπή SVG σε PNG για Docx
- `pymupdf` (`fitz`): καλύτερο post-processing στο PDF export

### Browser για PDF export
Για server-side PDF export πρέπει να είναι εγκατεστημένος τουλάχιστον ένας από τους παρακάτω browsers:

- Microsoft Edge
- Google Chrome
- Chromium

---

## Εγκατάσταση

1. Κατεβάστε το αρχείο της εφαρμογής, π.χ.:

```text
Ollama_Cloud_Chat_Studio_v4_New.py
```

2. Δημιουργήστε προαιρετικά virtual environment:

```bash
python -m venv .venv
```

3. Ενεργοποιήστε το virtual environment.

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

4. Εγκαταστήστε τα dependencies:

```bash
pip install beautifulsoup4 python-docx pillow pygments pypdf cairosvg pymupdf
```

5. Βεβαιωθείτε ότι έχετε διαθέσιμο το API key του Ollama Cloud.

---

## Εκτέλεση

Η βασική εκτέλεση είναι:

```bash
python Ollama_Cloud_Chat_Studio_v4_New.py
```

Αν όλα είναι σωστά, η εφαρμογή:

- ξεκινά τοπικό web server,
- βρίσκει διαθέσιμη θύρα,
- ανοίγει τον browser,
- και φορτώνει το UI του studio.

Αν δεν θέλετε αυτόματο άνοιγμα browser:

```bash
python Ollama_Cloud_Chat_Studio_v4_New.py --no-browser
```

Παράδειγμα αλλαγής port:

```bash
python Ollama_Cloud_Chat_Studio_v4_New.py --port 8788
```

Παράδειγμα φόρτωσης system prompt από εξωτερικό αρχείο:

```bash
python Ollama_Cloud_Chat_Studio_v4_New.py --system-prompt-file custom_system_prompt.txt
```

---

## Πρώτη ρύθμιση

### Επιλογή 1: API key από το UI

1. Ανοίξτε την εφαρμογή.
2. Στο αριστερό panel βρείτε το πεδίο **Ollama API Key**.
3. Επικολλήστε το API key σας.
4. Πατήστε **Save Key**.

### Επιλογή 2: API key από environment variable

**Windows (PowerShell)**

```powershell
$env:OLLAMA_API_KEY="ollama_xxx"
python Ollama_Cloud_Chat_Studio_v4_New.py
```

**Linux / macOS**

```bash
export OLLAMA_API_KEY="ollama_xxx"
python Ollama_Cloud_Chat_Studio_v4_New.py
```

### Επιλογή 3: API key στο settings file

Η εφαρμογή αποθηκεύει ρυθμίσεις στο:

```text
ollama_cloud_chat_settings.json
```

Παράδειγμα μορφής:

```json
{
  "ollama_api_key": "ollama_xxx",
  "active_prompt_profile": "scientific-technical",
  "custom_system_prompt": "",
  "active_visualization_engine": "auto",
  "updated_at": "2026-04-06 19:00:00"
}
```

---

## Αναλυτικός οδηγός χρήσης

## Διάταξη του UI

Το UI χωρίζεται σε δύο βασικά μέρη:

### Αριστερό panel
Περιέχει όλα τα controls ρύθμισης:

- επιλογή μοντέλου,
- ταξινόμηση μοντέλων,
- thinking mode,
- dual model ensemble,
- API key,
- prompt profile,
- visualization engine,
- system prompt,
- attachments,
- model parameters,
- session εργαλεία,
- export συνομιλίας,
- theme toggle.

### Κύριο panel συνομιλίας
Περιέχει:

- header με badges κατάστασης,
- panel realtime thinking,
- ιστορικό μηνυμάτων,
- message actions,
- composer για νέο prompt,
- stop / send controls.

---

## Επιλογή μοντέλου

### Model selector
Από το πεδίο **Μοντέλο Ollama** μπορείτε να επιλέξετε το cloud model που θα χρησιμοποιηθεί για την απάντηση.

### Model search
Το πεδίο αναζήτησης πάνω από τη λίστα χρησιμεύει για γρήγορο φιλτράρισμα όταν υπάρχουν πολλά μοντέλα.

### Model sort
Η ταξινόμηση μπορεί να γίνει με βάση:

- Overall
- Coding
- Reasoning
- Long Context / Max Length
- Vision
- Speed
- Newest

### Refresh Models
Αν θέλετε ενημέρωση του catalog, πατήστε **Refresh Models**.

Χρήσιμο όταν:

- προστέθηκαν νέα cloud models,
- θέλετε νεότερα metadata,
- θέλετε να φρεσκάρετε cache / ranking.

---

## Thinking Mode

Το **Thinking Mode** ελέγχει τον τρόπο με τον οποίο ζητείται reasoning / thinking από το επιλεγμένο μοντέλο.

### Επιλογές

- **Auto**: η εφαρμογή επιλέγει δυναμικά συμπεριφορά
- **On**: ζητά thinking όπου υποστηρίζεται
- **Off**: προσπαθεί να το απενεργοποιήσει
- **Low / Medium / High**: αυξανόμενη ένταση reasoning

### Επιβεβαίωση προφίλ
Το κουμπί **Επιβεβαίωση Profile** χρησιμοποιείται για να επιβεβαιώσετε το thinking support profile του τρέχοντος μοντέλου.

### Realtime thinking panel
Αν το μοντέλο επιστρέφει thinking stream, αυτό μπορεί να εμφανιστεί σε ξεχωριστό panel μέσα στο UI. Έτσι βλέπετε:

- την εξέλιξη της reasoning ροής,
- μεταδεδομένα thinking,
- και τελικό καθαρό answer body.

---

## Dual Model Ensemble

Η εφαρμογή μπορεί να χρησιμοποιήσει δεύτερο μοντέλο ως helper.

### Off
Χρησιμοποιείται μόνο το κύριο μοντέλο.

### Auto
Η εφαρμογή ανιχνεύει το task και διαλέγει βοηθητικό μοντέλο ανάλογα με το αν το αίτημα μοιάζει με:

- vision task,
- code task,
- long-context task,
- reasoning task,
- cross-check ανάγκη.

### Manual
Επιλέγετε εσείς το helper model από τη λίστα.

### Πότε έχει νόημα
Χρησιμοποιήστε ensemble όταν θέλετε:

- καλύτερη ανάλυση εικόνας,
- πιο ασφαλές code review,
- δεύτερη γνώμη σε reasoning,
- βοήθεια σε πολύ μεγάλα inputs,
- ή cross-check της κύριας απάντησης.

---

## Prompt Profile

Τα prompt profiles είναι προκαθορισμένες στρατηγικές system prompt.

### Apply Profile
Το κουμπί **Apply Profile** εφαρμόζει άμεσα το επιλεγμένο profile στο πεδίο System Prompt.

### Save Setup
Το **Save Setup** αποθηκεύει:

- ενεργό prompt profile,
- custom system prompt,
- ενεργό visualization engine.

### Ποιο profile να διαλέξω;

- **Scientific / Technical Expert**: η ασφαλής γενική επιλογή
- **Code Development / Production Engineering**: για υλοποίηση εφαρμογών και production code
- **Educational / Teacher Mode**: για μάθημα, θεωρία, βήμα-βήμα εξήγηση
- **Math & Physics Solver**: για λυμένες ασκήσεις, τύπους και μεθοδολογία
- **Code Reviewer / Debugger**: για bug hunting και τεχνική διάγνωση
- **Research / Structured Analysis**: για συγκριτική ανάλυση και τεκμηρίωση
- **Diagram & Visualization Mode**: όταν δίνετε έμφαση σε σχήματα και plots
- **Concise Engineer**: όταν θέλετε πιο σύντομες, πυκνές απαντήσεις

---

## Visualization Engine

Ορίζει τον τρόπο που θα καθοδηγείται το μοντέλο για οπτικοποιήσεις.

### Auto
Κατάλληλο για μικτή χρήση.

- SVG για εννοιολογικά / θεωρητικά σχήματα
- matplotlib για data plots και υπολογιστικά γραφήματα

### SVG / Diagrams
Προτιμήστε το όταν ζητάτε:

- flowcharts,
- block diagrams,
- εκπαιδευτικά διαγράμματα,
- αρχιτεκτονικά σχήματα,
- λογικά / θεωρητικά σχέδια.

### Python Plot / matplotlib
Προτιμήστε το όταν ζητάτε:

- γραφήματα συναρτήσεων,
- scientific plots,
- scatter / bar / histogram,
- υπολογιστική οπτικοποίηση,
- plots που θέλετε να επαναπαράγετε σε Python.

---

## System Prompt

Το πεδίο **System Prompt** περιέχει την ενεργή prompt στρατηγική της συνεδρίας.

Μπορείτε να:

- το τροποποιήσετε χειροκίνητα,
- να το επαναφέρετε στο ενεργό profile,
- να το αντιγράψετε,
- να το αποθηκεύσετε στο settings file.

### Reset Prompt
Επαναφέρει το prompt στο τρέχον prompt profile.

### Copy Prompt
Αντιγράφει το πλήρες system prompt στο clipboard.

---

## Συνημμένα αρχεία

Η εφαρμογή υποστηρίζει file picker αλλά και **drag & drop** σε όλη την επιφάνεια.

### Τι είδη αρχείων δέχεται

Ενδεικτικά:

- εικόνες (`png`, `jpg`, `jpeg`, `webp`, `bmp`, `gif`, `tif`, `tiff`)
- text files (`txt`, `md`, `json`, `yaml`, `xml`, `html`, `css`)
- source code (`py`, `js`, `ts`, `java`, `c`, `cpp`, `cs`, `go`, `rs`, `php`, `rb`, `swift`, `kt`, `sql` κ.ά.)
- tabular text (`csv`, `tsv`)
- `pdf`

### Συμπεριφορά αρχείων

- **Εικόνες**: στέλνονται natively σε vision-capable models όταν είναι εφικτό
- **Text / code / PDF**: εξάγεται κείμενο / excerpt για context injection

### Όρια

- έως **8 αρχεία** ανά μήνυμα
- έως **15 MB** ανά αρχείο
- truncation σε πολύ μεγάλα text contexts

### Καθαρισμός αρχείων
Το κουμπί **Καθαρισμός** αφαιρεί τα επιλεγμένα attachments από το τρέχον prompt.

---

## Παράμετροι μοντέλου

Στο panel **Παράμετροι μοντέλου** μπορείτε να ελέγξετε:

### Temperature
Ρυθμίζει τη δημιουργικότητα / τυχαιότητα.

- χαμηλή τιμή: πιο σταθερές απαντήσεις
- υψηλή τιμή: πιο ελεύθερες / δημιουργικές απαντήσεις

### Top-P
Ελέγχει nucleus sampling.

### Seed
Για πιο αναπαραγώγιμες απαντήσεις.

- `-1`: τυχαίο
- `>= 0`: σταθερό seed

### Max Length (`num_ctx`)
Ορίζει custom context window για το τρέχον μοντέλο.

- κενό πεδίο: auto / default
- custom τιμή: όταν θέλετε συγκεκριμένο context budget

### Reset / Auto

- **Reset**: επαναφέρει βασικές παραμέτρους
- **Auto** στο `num_ctx`: αφαιρεί custom context override

---

## Χρήση της συνομιλίας

### Πληκτρολόγηση prompt
Γράψτε το prompt σας στο κάτω textarea.

### Συντομεύσεις πληκτρολογίου

- `Enter`: αποστολή
- `Shift + Enter`: νέα γραμμή
- `Ctrl + Enter`: εναλλακτική αποστολή

### Αποστολή / Διακοπή

- **Αποστολή**: στέλνει το prompt
- **Stop**: διακόπτει το streaming της απάντησης

### Auto-scroll
Το **Auto-Scroll** ελέγχει αν το chat ακολουθεί αυτόματα τα νέα chunks.

### Scroll to bottom
Όταν έχετε μετακινηθεί προς τα πάνω, εμφανίζεται κουμπί για γρήγορη επιστροφή στο τέλος.

---

## Session εργαλεία

### Clear Chat
Καθαρίζει:

- το ιστορικό συνομιλίας,
- τα προσωρινά uploads,
- generated artifacts της συνεδρίας.

### Reload Session
Ξαναφορτώνει το ιστορικό από τον server.

### Export `.md`
Εξάγει ολόκληρη τη συνομιλία σε αρχείο Markdown.

### Theme Toggle
Αλλάζει το UI ανάμεσα σε light και dark theme.

---

## Εξαγωγές απαντήσεων assistant

Σε κάθε απάντηση assistant υπάρχουν message-level εργαλεία για export.

### Export PDF
Χρησιμοποιήστε το όταν θέλετε printable export της συγκεκριμένης απάντησης.

Χαρακτηριστικά:

- printable HTML pipeline,
- headless browser PDF generation,
- post-processing / polish,
- metadata στο τελικό PDF,
- προσπάθεια καλής απόδοσης Markdown, SVG και μαθηματικών.

### Export Docx
Χρησιμοποιήστε το όταν θέλετε επεξεργάσιμο έγγραφο Word.

Χαρακτηριστικά:

- μετατροπή HTML fragment σε `.docx`,
- διατήρηση headings / paragraphs / lists,
- χειρισμός μαθηματικών fallback,
- ενσωμάτωση εικόνων όπου είναι εφικτό.

### Πότε να προτιμήσω τι

- **PDF**: τελική παρουσίαση, εκτύπωση, αρχειοθέτηση
- **Docx**: μεταγενέστερη επεξεργασία, σχολιασμός, διορθώσεις

---

## Python code blocks μέσα στο chat

Όταν το assistant επιστρέφει Python code blocks, το studio μπορεί να προσφέρει επιπλέον εργαλεία.

### Save `.py`
Αποθηκεύει τον κώδικα ως αρχείο Python.

### Run
Προσπαθεί να εκτελέσει το block σε νέο terminal.

### Render Plot
Αν ο κώδικας είναι κατάλληλος για matplotlib plotting, η εφαρμογή μπορεί να κάνει ασφαλές render και να παράγει εικόνα από το plot.

### Σημαντική σημείωση
Το ασφαλές plot rendering δεν επιτρέπει αυθαίρετη χρήση βιβλιοθηκών ή επικίνδυνων κλήσεων. Είναι σχεδιασμένο για ελεγχόμενα matplotlib-based plots.

---

## Αρχεία και αποθηκεύσεις της εφαρμογής

Η εφαρμογή χρησιμοποιεί διάφορα αρχεία / φακέλους δίπλα στο κύριο `.py` ή σε temp directories.

### Βασικά αρχεία

```text
ollama_cloud_chat_settings.json
ollama_cloud_model_registry_cache.json
```

### Βασικοί φάκελοι

```text
_chat_uploads
_generated_code_blocks
_generated_media
```

### Τι αποθηκεύεται πού

- `_chat_uploads`: προσωρινά ή ενεργά attachments της συνεδρίας
- `_generated_code_blocks`: αποθηκευμένα `.py` scripts από code blocks
- `_generated_media`: rendered plots / generated media
- `ollama_cloud_chat_settings.json`: API key και persistent settings
- `ollama_cloud_model_registry_cache.json`: cache του catalog μοντέλων

---

## Εξαγωγές και generated artifacts

### PDF
Για να λειτουργήσει σωστά το PDF export:

- πρέπει να υπάρχει Edge / Chrome / Chromium,
- το printable HTML fragment να είναι έγκυρο,
- και να είναι διαθέσιμες οι απαραίτητες βιβλιοθήκες για το polish pipeline όπου χρειάζεται.

### Docx
Για καλύτερη εμπειρία Docx export προτείνονται:

- `python-docx`
- `Pillow`
- `cairosvg` όταν υπάρχουν SVG στοιχεία που χρειάζεται να μετατραπούν

### Plot rendering
Για plot rendering απαιτούνται:

- Python interpreter διαθέσιμος στο σύστημα
- `matplotlib`
- προαιρετικά `numpy` / `pandas` αν τα plots σας το χρειάζονται

---

## Παράμετροι εκκίνησης από γραμμή εντολών

Η εφαρμογή υποστηρίζει:

```bash
python Ollama_Cloud_Chat_Studio_v4_New.py \
  --port 8765 \
  --host 127.0.0.1 \
  --log-level INFO \
  --system-prompt-file custom_system_prompt.txt
```

### Διαθέσιμες επιλογές

- `--port`: θύρα του web server
- `--host`: host address
- `--no-browser`: να μη γίνει αυτόματο άνοιγμα browser
- `--log-level`: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `--system-prompt-file FILE`: φόρτωση system prompt από `.txt`

---

## Troubleshooting

## 1. Δεν απαντά το chat

Ελέγξτε:

- αν υπάρχει σωστό **Ollama API Key**,
- αν έχετε σύνδεση στο διαδίκτυο,
- αν το μοντέλο είναι διαθέσιμο στο cloud catalog,
- αν το request δεν ξεπερνά limits context / attachments.

## 2. Δεν φορτώνονται μοντέλα

Δοκιμάστε:

- **Refresh Models**
- έλεγχο δικτύου / DNS
- έλεγχο firewall / proxy
- διαγραφή ή ανανέωση του `ollama_cloud_model_registry_cache.json`

## 3. Δεν λειτουργεί το PDF export

Ελέγξτε αν υπάρχει εγκατεστημένος:

- Microsoft Edge
- Google Chrome
- ή Chromium

## 4. Δεν λειτουργεί το Docx export

Εγκαταστήστε:

```bash
pip install python-docx pillow cairosvg
```

## 5. Το Run σε Python code block αποτυγχάνει

Πιθανές αιτίες:

- δεν υπάρχει διαθέσιμος Python interpreter,
- το block έχει syntax error,
- τρέχετε packaged `.exe` χωρίς σωστό system Python.

## 6. Τα attachments δεν περνούν σωστά

Ελέγξτε:

- πλήθος αρχείων,
- μέγεθος αρχείων,
- αν το αρχείο είναι σε υποστηριζόμενο format,
- αν το prompt σας είναι ήδη πολύ μεγάλο.

## 7. Το thinking mode δεν λειτουργεί όπως ζητήθηκε

Ορισμένα μοντέλα δεν υποστηρίζουν όλα τα think modes με τον ίδιο τρόπο. Η εφαρμογή προσπαθεί αυτόματο fallback.

---

## Χρήσιμες πρακτικές

### Για τεχνική συγγραφή
Χρησιμοποιήστε:

- profile: **Scientific / Technical Expert**
- visualization: **Auto** ή **SVG**
- χαμηλό προς μεσαίο temperature

### Για παραγωγή κώδικα
Χρησιμοποιήστε:

- profile: **Code Development / Production Engineering**
- ensemble: **Auto** ή **Manual** με code-oriented helper
- visualization: **Python Plot** αν ζητάτε plots

### Για debugging
Χρησιμοποιήστε:

- profile: **Code Reviewer / Debugger**
- ensemble: **Auto** ή **Manual**
- attachments: ανεβάστε το σχετικό source file ή log

### Για μαθηματικά / φυσική
Χρησιμοποιήστε:

- profile: **Math & Physics Solver**
- thinking mode: **On** ή **Medium**
- export: **PDF** όταν θέλετε τελικό αρχείο παρουσίασης

### Για εκπαιδευτικό υλικό
Χρησιμοποιήστε:

- profile: **Educational / Teacher Mode**
- visualization: **SVG** ή **Auto**
- export: **Docx** αν θέλετε μεταγενέστερη επεξεργασία

---

## Περιορισμοί

- Η βασική λειτουργία συνομιλίας εξαρτάται από το **Ollama Cloud API**.
- Το PDF export εξαρτάται από εγκατεστημένο browser με headless print-to-pdf δυνατότητα.
- Πολύ μεγάλα prompts ή πολλά attachments μπορεί να ξεπεράσουν limits request / context.
- Ορισμένα think modes ή model options μπορεί να μην υποστηρίζονται ομοιόμορφα από όλα τα μοντέλα.
- Το plot renderer είναι περιορισμένο σκόπιμα για λόγους ασφάλειας.

---

## Προτεινόμενη δομή repository στο GitHub

```text
.
├── Ollama_Cloud_Chat_Studio_v4_New.py
├── README.md
├── requirements.txt
├── LICENSE
└── screenshots/
```

### Προαιρετικό `requirements.txt`

```text
beautifulsoup4
python-docx
pillow
pygments
pypdf
cairosvg
pymupdf
matplotlib
numpy
pandas
```

---

## Πρόταση για GitHub screenshots

Αν πρόκειται να ανεβάσετε το project δημόσια, είναι καλή ιδέα να προσθέσετε εικόνες όπως:

- αρχική οθόνη της εφαρμογής,
- sidebar με settings,
- thinking panel,
- παράδειγμα συνομιλίας,
- export PDF / Docx,
- παράδειγμα SVG ή plot rendering.

Έτσι το repository θα είναι πιο κατανοητό και πιο επαγγελματικό.

---

## Άδεια χρήσης και attribution

Αν το ανεβάσετε στο GitHub, φροντίστε να προσθέσετε:

- ένα αρχείο `LICENSE`,
- σαφή αναφορά του δημιουργού,
- και, αν θέλετε, changelog ή release notes.

---

## Σύντομη εκδοχή για γρήγορη εκκίνηση

```bash
pip install beautifulsoup4 python-docx pillow pygments pypdf cairosvg pymupdf matplotlib numpy pandas
python Ollama_Cloud_Chat_Studio_v4_New.py
```

Έπειτα:

1. Βάλτε το **Ollama API Key**.
2. Πατήστε **Save Key**.
3. Επιλέξτε μοντέλο.
4. Γράψτε prompt.
5. Προαιρετικά ανεβάστε αρχεία.
6. Στείλτε το μήνυμα.
7. Εξάγετε την απάντηση σε **PDF**, **Docx** ή **Markdown**.

---



