# LTC — Capitolo 4: il premio puro proiettato sulla platea reale

> Sequenza naturale dell'[origine del progetto](00_origine_evento_attuari.md): replica la logica dell'esempio numerico dell'Ordine degli Attuari (rendita LTC 500 €/mese, premio puro 74-113 €/anno) sulla piramide proiettata Leslie-Rogers due sessi. Implementazione: `src/ltc_attuariale.py`, esecuzione: `python3 src/ltc_attuariale.py`.

## 1. Il modello

- **Platea iniziale**: 10 milioni di aderenti alla previdenza complementare, con struttura per età e sesso della fascia nazionale 25-64 scalata (ipotesi dichiarata: la struttura reale degli aderenti è più vicina agli occupati; l'effetto robusto del modello è la **dinamica** del premio, non il livello puntuale)
- **Rendita vitalizia**: 500 €/mese (6.000 €/anno, come nell'esempio dell'Ordine)
- **Prudenza** (assunti dell'esempio): nessun recupero dell'autosufficienza; esclusi i non autosufficienti all'avvio — i claimants maturano solo per incidenza successiva
- **Incidenza netta**: approssimata dal gradiente della prevalenza parametrica del [capitolo 1](08_ltc_capitolo1.md) — upper bound prudenziale (le bande generano "spike" ai bordi: la distribuzione annua è approssimata, lo stock cumulativo è conservativo)
- **Sistema finanziario**: ripartizione del costo annuo delle rendite (premio puro, senza caricamenti né margini di sicurezza)
- **Contribuenti**: aderenti 25-64; due scenari di platea:
  - **A) platea costante** (coorte chiusa, nessun nuovo ingresso)
  - **B) adesioni automatiche** (ingressi annuali = la coorte nazionale dei 25enni scalata alla quota aderenti)

## 2. Risultati

| Scenario | 2026 | 2056 | 2081 |
|---|---|---|---|
| **Platea costante (chiusa)** | 21 € | 438 € | **1.409 €** |
| **Adesioni automatiche** | 21 € | 220 € | **253 €** |
| Benchmark Ordine Attuari (equilibrio) | — | — | 113 € (costante) / 74 € (crescente) |

## 2-bis. Scenario indicizzato (rivalutazione della rendita al 2% annuo)

L'indicizzazione della rendita (raccomandata dal modello tedesco: adeguamento annuo all'inflazione di fondo dal 2029, vedi [00](00_origine_evento_attuari.md)) cambia l'ordine di grandezza nominale del premio ma non la sostanza demografica:

| Scenario (adesioni automatiche) | 2026 | 2056 | 2081 |
|---|---|---|---|
| Rendita nominale fissa (500 €/mese) | 21 € | 220 € | 253 € |
| Rendita indicizzata al **2%** annuo | 21 € | 398 € | 750 € |
| Rendita indicizzata al **3%** annuo | 21 € | 534 € | **1.284 €** |
| Qualsiasi, deflata ai prezzi 2026 | 21 € | 220 € | 253 € |

**Letture**:

1. **L'indicizzazione è puro effetto-prezzo**: il premio reale deflato al 2% coincide esattamente con lo scenario non indicizzato (verificato anche da un test di consistenza) — la demografia sottostante non cambia, cambia solo l'unità di conto
2. **Il moltiplicatore nominale è però rilevante per la sostenibilità percepita**: a 2% annuo per 55 anni il fattore è ~3x (746 vs 251 €/anno al 2081); **al 3% sale a ~5x (1.275 €/anno)** — un'inflazione italiana anche solo un punto sopra il target di Francoforte, protratta per decenni, raddoppia il costo nominale dell'opzione indicizzazione. Se i salari indicizzano all'inflazione, il peso **reale** è invariato; ma ogni gap retribuzione-inflazione (stagnazione reale dei salari, come accaduto in Italia negli anni 2012-2019) si traduce integralmente in aumento del carico relativo
3. **Va quantificato il costo dell'indicizzazione come opzione separata** — esattamente il criterio adottato dal Pnog tedesco: importi fissi fino al 2028, poi indicizzazione dal 2029 — il costo differito è la scelta politica esplicita, non un dettaglio tecnico

## 3. Letture

1. **L'ordine di grandezza del 2026 è plausibile** (21 €/anno per fondo appena costituito: pochissimi claimants) e converrà verso i tre cifre man mano che il fondo matura — ma **la traiettoria è il dato nuovo** rispetto all'esempio dell'Ordine: il livello di equilibrio non è raggiunto in regime stazionario, è attraversato in salita mentre la coorte fondatrice invecchia.

2. **La differenza 74 vs 113 € dell'Ordine ordinalmente confermata e capovolta nel tempo**: la platea che cresce (adesioni automatiche) mantiene più contribuenti a fronte di claimants crescenti e **stabilizza il premio a ~250 €/anno al 2081** (influsso regolare di 25enni). La platea chiusa, invece, **satura**: i contribuenti si spengono e il premio esplode a 1.397 €/anno al 2081 — cinque volte il livello con adesioni. Il sistema funziona solo se la platea si rinnova: è la versione attuariale dello stesso risultato demografico del [capitolo 3](10_ltc_capitolo3_informale.md) caregiver gap (non colmabile chiudendo il sistema).

3. **Il perché la stima prudenziale è ~2x il benchmark dell'Ordine**: l'esempio dell'Ordine usa incidenze da basi attuariali multistato (ANIA-Sapienza), che includono la mortalità selettiva e la costruzione meticolosa dell'ingresso in claimancy; il nostro gradiente di prevalenza è un upper bound che accumula tutta la NAS attesa per età senza attenuazioni — coerente con l'assunzione "nessun recupero", ma senza raffinamenti. I due risultati **raccontano la stessa storia**: noi mostriamo la dinamica su una piramide specifica, l'Ordine il livello attuariale di equilibrio ben calibrato.

4. **Il messaggio per il tavolo tecnico dell'Ordine (prossimo passo previsto dall'evento stesso)**: la proposta di inserire la LTC nella previdenza complementare è sostenibile solo se accompagnata da **adesioni automatiche e continue** — i dati mostrano che la platea ingrigente senza ricambio produce un premio insostenibile anche partendo da 10 milioni di aderenti. La parabola del premio costante (funzione del tempo) è il grafico che manca all'esempio numerico: ora è calcolabile direttamente da `python3 src/ltc_attuariale.py`.

## 4. Limiti e passi successivi

- **Struttura della platea**: scalata dalla popolazione 25-64, non dagli aderenti reali (dati COVIP per fascia quando integrati — attenzione COVIP pubblica adesioni aggregate); la struttura occupati è la prossima approssimazione, ottenibile per differenza fra forze lavoro e popolazione
- **Incidenza**: da sostituire con le tavole multistato ANIA-Sapienza aggiornate (i claimants incrementano per incidenza netta vera, non per gradiente di prevalenza — che resta la forma prudenziale dichiarata)
- **Assicurazione del rischio longevità morbidità**: nessun caricamento, nessuna gestione dell'asimmetria di mortalità (NAS muoiono prima: qui la sopravvivenza applicata ai claimants è quella generale, non quella specifica NAS — un secondo livello prudenziale che amplifica la stima)
- **Rischio di sistema**: la rendita è nominale (nessuna indicizzazione); l'Ordine aveva raccomandato prestazioni indicizzate come la Germania dal 2029 (vedi [00](00_origine_evento_attuari.md) § De Tommaso) — il costo dell'indicizzazione è ora quantificato nello scenario 2-bis (~3x nominale a 55 anni)
