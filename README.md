# Ollama Cloud Chat Studio v3.0

Μια desktop-style εφαρμογή σε Python που ανοίγει σε browser και προσφέρει σύγχρονο περιβάλλον συνομιλίας με μοντέλα **Ollama Cloud / Direct API**, με έμφαση σε παραγωγή επαγγελματικού κώδικα, διαχείριση code blocks, εκτέλεση Python scripts και ευέλικτο dual-model workflow.

## Βασικά χαρακτηριστικά

- Σύνδεση με **Ollama Cloud / Direct API**
- Φόρτωση και εμφάνιση official direct API models
- Επιλογή κύριου μοντέλου από το GUI
- **Dual Model Ensemble**
  - Off
  - Auto
  - Manual
- Επιλογή δεύτερου helper model από λίστα
- Αναζήτηση μοντέλων από το GUI
- Thinking mode όπου υποστηρίζεται
- Προβολή απάντησης σε καθαρό chat UI
- Υποστήριξη για code blocks
- Κουμπί **Copy**
- Κουμπί **Save**
- Κουμπί **Run** για Python code blocks
- Αυτόματη εξαγωγή ονομάτων αρχείων `.py` από την περιγραφή της εφαρμογής
- Το όνομα αρχείου εμφανίζεται δίπλα στο κουμπί αποθήκευσης και εκτέλεσης
- Αποθήκευση generated Python αρχείων με καθαρά filenames
- Εκτέλεση Python blocks σε νέο terminal
- Καλύτερη συμπεριφορά στο packaged `.exe` με αναζήτηση πραγματικού Python interpreter για το `Run`
- Auto-exit του local server όταν κλείσει το browser window/tab της εφαρμογής
- Ρυθμίσεις εφαρμογής σε τοπικό αρχείο JSON
- Δυνατότητα build σε `.exe`
- Δυνατότητα δημιουργίας installer με Inno Setup

---

## Σκοπός της εφαρμογής

Η εφαρμογή έχει σχεδιαστεί για χρήστες που θέλουν:
- γρήγορη πρόσβαση σε cloud LLMs,
- παραγωγή πιο επαγγελματικού και ολοκληρωμένου κώδικα,
- εύκολη αποθήκευση και εκτέλεση code blocks,
- καλύτερο έλεγχο στο ποιο μοντέλο απαντά και ποιο βοηθά ως helper model.

Είναι ιδιαίτερα χρήσιμη για:
- Python development
- code generation
- debugging
- δημιουργία μικρών εφαρμογών
- εκπαιδευτική χρήση
- παραγωγή παραδοτέων αρχείων `.py`

---

## Απαιτήσεις

- Python 3.10+  
  Προτείνεται Python 3.12
- Σύνδεση στο διαδίκτυο
- Έγκυρο API key για Ollama Cloud / Direct API

### Προαιρετικές βιβλιοθήκες
- `pypdf` για υποστήριξη PDF
- `Pillow` για image handling όπου απαιτείται

---

## Εγκατάσταση

### 1. Κλωνοποίηση αποθετηρίου

```bash
git clone https://github.com/USERNAME/ollama-cloud-chat-studio.git
cd ollama-cloud-chat-studio
