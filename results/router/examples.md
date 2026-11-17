# Side-by-side examples

> Historical outputs from the original always-context experiment. Route labels do not always describe the examples actually supplied. See [the audit](../audit/report.md). References to what a CAT tool shows refer only to this project's configured fuzzy approximation.

### Real segment win 1

**New segment:** Irbesartan Hydrochlorothiazide Winthrop 300 mg/ 12.5 mg tablets.

**Best fuzzy match (67% → a CAT tool shows nothing):** CoAprovel 150 mg/ 12.5 mg tablets.

**Semantic match (similarity 92, judged reusable: partial):**  
EN: Irbesartan Hydrochlorothiazide Winthrop 300 mg/ 25 mg film-coated tablets.  
ES: Irbesartan Hydrochlorothiazide Winthrop, 300 mg/ 25 mg, comprimidos recubiertos con película.

| | translation |
|---|---|
| zero-shot (today) | Irbesartán hidroclorotiazida Winthrop 300 mg/12,5 mg comprimidos. |
| **semantic RAG** | Irbesartan Hydrochlorothiazide Winthrop, 300 mg/ 12,5 mg, comprimidos. |
| human reference | Irbesartan Hydrochlorothiazide Winthrop, 300 mg/ 12,5 mg, comprimidos. |

Localization judge: **rag** better. The new segment says just 'tablets' (not film-coated), so 'comprimidos' is accurate in both; A keeps the approved product name 'Irbesartan Hydrochlorothiazide Winthrop' and the TM's comma-separated format, whereas B translates/alters the approved product name to 'Irbesartán hidroclorotiazida' and drops the commas.  
Generic judge: **rag** better. Both are accurate, but A keeps the product name exactly as the authorised (invented) name, matching the human reference, while B alters the name by translating it to Spanish ('Irbesartán hidroclorotiazida'), which changes the trade name and is not appropriate for a product name in this context.

### Real segment win 2

**New segment:** (3) Briefly press and release red button.

**Best fuzzy match (70% → a CAT tool shows nothing):** Briefly press and release red button.

**Semantic match (similarity 92, judged reusable: full):**  
EN: Briefly press and release red button.  
ES: Presione brevemente el botón rojo y suéltelo.

| | translation |
|---|---|
| zero-shot (today) | (3) Pulse brevemente y suelte el botón rojo. |
| **semantic RAG** | (3) Presione brevemente el botón rojo y suéltelo. |
| human reference | (3) Presione brevemente el botón rojo y suéltelo. |

Localization judge: **rag** better. Both translations are accurate, but A reuses the approved TM phrasing exactly ("Presione brevemente el botón rojo y suéltelo"), while B substitutes "Pulse" and restructures the sentence without any need.  
Generic judge: **tie** better. Both translations convey the same instruction accurately, with 'presione' and 'pulse' both acceptable in Spanish regulatory style and nothing added or lost, so neither has a meaningful advantage.

### Real segment win 3

**New segment:** Vimpat 15 mg/ ml syrup Lacosamide

**Best fuzzy match (56% → a CAT tool shows nothing):** Vimpat 10 mg/ml solution for infusion Lacosamide

**Semantic match (similarity 81, judged reusable: partial):**  
EN: Vimpat 10 mg/ml solution for infusion Lacosamide  
ES: Vimpat 10 mg/ml solución para perfusión Lacosamida

| | translation |
|---|---|
| zero-shot (today) | Vimpat jarabe 15 mg/ml Lacosamida |
| **semantic RAG** | Vimpat 15 mg/ ml jarabe Lacosamida |
| human reference | Vimpat 15 mg/ ml jarabe Lacosamida |

Localization judge: **rag** better. Both are accurate (15 mg/ml, jarabe, Lacosamida), but A keeps the approved TM word order 'Vimpat [strength] [form] Lacosamida', while B moves the form ahead of the strength, departing from the approved phrasing.  
Generic judge: **rag** better. Both translations are accurate, but A keeps the source order and format (Vimpat 15 mg/ ml jarabe), matching the reference and the English segment, whereas B reorders the elements and changes the spacing ('jarabe 15 mg/ml'), which is acceptable but deviates from the source.

### Real segment win 4

**New segment:** It is not known whether oseltamivir or the active metabolite are excreted in human milk.

**Best fuzzy match (69% → a CAT tool shows nothing):** Lactation It is not known whether azacitidine or its metabolites are excreted in human milk.

**Semantic match (similarity 83, judged reusable: partial):**  
EN: It is not known whether this medicinal products or its metabolites are excreted in human milk.  
ES: Se desconoce si este fármaco o sus metabolitos se excretan en la leche humana.

| | translation |
|---|---|
| zero-shot (today) | No se sabe si el oseltamivir o su metabolito activo se excretan en la leche materna. |
| **semantic RAG** | Se desconoce si oseltamivir o el metabolito activo se excretan en la leche humana. |
| human reference | Se desconoce si oseltamivir o el metabolito activo se excretan en la leche humana. |

Localization judge: **rag** better. Both translations convey the meaning accurately, but A reuses the approved phrasing 'Se desconoce si... se excretan en la leche humana', while B replaces it with 'No se sabe si' and 'leche materna', which departs from the approved terminology.  
Generic judge: **rag** better. Both are accurate, but A matches EU SmPC standard phrasing ("Se desconoce si...", "leche humana", no article before the INN, "el metabolito activo"), while B uses the less formal "No se sabe", adds the article "el" before oseltamivir, changes "the active metabolite" to "su metabolito activo", and uses "leche materna" instead of the source's "human milk".

### Real segment win 5

**New segment:** At least one LVEF drop of ≥ 15% from baseline and below 50% a

**Best fuzzy match (69% → a CAT tool shows nothing):** Symptomatic CHF Confirmed LVEF drops of ≥ 15% from Baseline and below 50%

**Semantic match (similarity 83, judged reusable: partial):**  
EN: Symptomatic CHF Confirmed LVEF drops of ≥ 15% from Baseline and below 50%  
ES: Descenso confirmado de la FEVI ≥ 15% respecto del valor basal y por debajo del 50%.

| | translation |
|---|---|
| zero-shot (today) | Al menos una disminución de la FEVI de ≥ 15 % desde el valor basal y por debajo del 50 % a |
| **semantic RAG** | Al menos un descenso de la FEVI ≥ 15% respecto del valor basal y por debajo del 50% a |
| human reference | Al menos un descenso en la FEVI ≥ 15% respecto del valor basal y por debajo del 50%. a |

Localization judge: **rag** better. Both are accurate, but B reuses the approved TM phrasing (descenso, de la FEVI, respecto del valor basal, 15%/50% format) while A substitutes disminución, desde el valor basal and spaced percentages.  
Generic judge: **rag** better. Both translations are accurate and keep the numbers, the 'at least one' condition and the trailing footnote marker 'a', but B uses the more natural regulatory phrasing 'respecto del valor basal' and matches the reference, whereas A uses the less idiomatic 'desde el valor basal'.

### Real segment win 6

**New segment:** Unit dose blister packs of 56 x 1 tablets for delivery in hospitals are also available.

**Best fuzzy match (68% → a CAT tool shows nothing):** Unidose blister packs of 56 x 1 film-coated tablet for delivery in hospitals are also available.

**Semantic match (similarity 92, judged reusable: partial):**  
EN: Unidose blister packs of 56 x 1 film-coated tablet for delivery in hospitals are also available.  
ES: También se encuentran disponibles en envases de 56 x 1 comprimido recubierto con película que contienen blisters unidosis para su suministro en hospitales.

| | translation |
|---|---|
| zero-shot (today) | También están disponibles blísteres de dosis unitaria de 56 x 1 comprimidos para suministro hospitalario. |
| **semantic RAG** | También se encuentran disponibles envases con blisters unidosis de 56 x 1 comprimidos para su suministro en hospitales. |
| human reference | También se encuentra disponible en envases de 56 x 1 comprimidos para su suministro en hospitales. |

Localization judge: **rag** better. Both are accurate to the new segment, which lacks 'film-coated', but A reuses the approved terms 'blisters unidosis', 'envases' and 'para su suministro en hospitales', while B substitutes 'dosis unitaria', 'blísteres' and 'suministro hospitalario'.  
Generic judge: **rag** better. Both translations convey the meaning accurately, but A uses the more standard EU Spanish packaging phrasing ('envases con blisters unidosis ... para su suministro en hospitales'), closer to the reference, while B's 'blísteres de dosis unitaria' and the shortened 'suministro hospitalario' are slightly less conventional.

### Reworded TM entry (paraphrase) win 1

**New segment:** Patients who take opioids like fentanyl over and over can become tolerant and physically or psychologically dependent.

**Best fuzzy match (20% → a CAT tool shows nothing):** Patients who take Humira must be given the special alert card that summarises the safety information about the medicine.

**Semantic match (similarity 88, judged reusable: partial):**  
EN: Upon repeated administration of opioids such as fentanyl, tolerance and physical and/ or psychological dependence may develop.  
ES: La administración repetida de opioides como fentanilo, puede producir tolerancia y dependencia física y/ o fisiológica.

| | translation |
|---|---|
| zero-shot (today) | Los pacientes que toman opioides como el fentanilo de forma repetida pueden desarrollar tolerancia y dependencia física o psicológica. |
| **semantic RAG** | Los pacientes que toman opioides como fentanilo repetidamente pueden desarrollar tolerancia y dependencia física o psicológica. |

Localization judge: **rag** better. Both are accurate (correctly using 'psicológica' despite the TM's 'fisiológica' error), but A keeps the approved phrase 'opioides como fentanilo' whereas B adds 'el' and the wordier 'de forma repetida'.  
Generic judge: **zero_shot** better. Both translations convey the meaning accurately (repeated use, tolerance, physical or psychological dependence), but B is more natural and idiomatic in Spanish regulatory style, using 'como el fentanilo' with the article and 'de forma repetida'.

### Reworded TM entry (restructure) win 2

**New segment:** Tolerance and physical and/or psychological dependence may develop when opioids such as fentanyl are given repeatedly.

**Best fuzzy match (32% → a CAT tool shows nothing):** Tolerance, physical or psychological dependence may develop if you use Fentanyl-ratiopharm for a longer period.

**Semantic match (similarity 95, judged reusable: partial):**  
EN: Upon repeated administration of opioids such as fentanyl, tolerance and physical and/ or psychological dependence may develop.  
ES: La administración repetida de opioides como fentanilo, puede producir tolerancia y dependencia física y/ o fisiológica.

| | translation |
|---|---|
| zero-shot (today) | Puede desarrollarse tolerancia y dependencia física y/o psicológica cuando se administran repetidamente opioides como el fentanilo. |
| **semantic RAG** | La administración repetida de opioides como fentanilo puede producir tolerancia y dependencia física y/o psicológica. |

Localization judge: **rag** better. Both are accurate (correctly using 'psicológica' rather than the TM's erroneous 'fisiológica'), but A reuses the approved phrasing and structure ('La administración repetida de opioides como fentanilo... puede producir tolerancia y dependencia...') while B rewords it unnecessarily.  
Generic judge: **zero_shot** better. Both translations convey the meaning accurately, but B stays closer to the source structure and 'may develop' wording, and uses the natural 'el fentanilo' as in EU Spanish SmPCs, whereas A omits the article and recasts the sentence as a nominalization.

### Reworded TM entry (restructure) win 3

**New segment:** Turn the pump clockwise after pressing it onto the top of the bottle, until it clicks tightly into place.

**Best fuzzy match (57% → a CAT tool shows nothing):** Press the pump onto the top of the bottle, and turn it clockwise until it clicks tightly into place.

**Semantic match (similarity 98, judged reusable: partial):**  
EN: Press the pump onto the top of the bottle, and turn it clockwise until it clicks tightly into place.  
ES: Ajuste la bomba con la boca del frasco y enrosque con fuerza en el sentido de las agujas del reloj hasta que haga clic y ajuste perfectamente.

| | translation |
|---|---|
| zero-shot (today) | Gire la bomba en sentido horario después de presionarla sobre la parte superior del frasco, hasta que encaje firmemente en su lugar. |
| **semantic RAG** | Enrosque la bomba en el sentido de las agujas del reloj después de ajustarla con la boca del frasco, hasta que haga clic y ajuste perfectamente. |

Localization judge: **rag** better. Both translations convey the new segment's meaning and sequence accurately, but A reuses the approved TM phrasing (ajustar con la boca del frasco, enrosque, en el sentido de las agujas del reloj, haga clic y ajuste perfectamente), while B substitutes different terms (presionarla sobre la parte superior, sentido horario, encaje firmemente) for the same concepts.  
Generic judge: **zero_shot** better. B accurately conveys pressing the pump onto the top of the bottle, turning it clockwise until it clicks firmly into place, in natural regulatory Spanish, whereas A mistranslates 'pressing it onto the top' as 'ajustarla con la boca del frasco', uses the awkward 'haga clic', and adds 'enrosque' (screw), which changes the action.

### Where RAG lost 1

**New segment:** Unopened pre-filled syringes may be kept un-refrigerated but below 25oC for a single maximum period of 5 days.

**Best fuzzy match (26% → a CAT tool shows nothing):** In daylight conditions complete efficacy is guaranteed for a period of three days.

**Semantic match (similarity 85, judged reusable: none):**  
EN: The syringe can be removed from the refrigerator and left at room temperature for a single period of maximum 3 days (but not above 25°C).  
ES: Conservar la jeringa precargada en el embalaje exterior para protegerla de la luz.

| | translation |
|---|---|
| zero-shot (today) | Las jeringas precargadas sin abrir pueden conservarse sin refrigeración, pero a una temperatura inferior a 25 °C, durante un único período máximo de 5 días. |
| **semantic RAG** | Las jeringas precargadas sin abrir pueden conservarse fuera de la nevera, pero a una temperatura inferior a 25 °C, durante un único período máximo de 5 días. |
| human reference | Las jeringas precargadas sin abrir pueden mantenerse sin refrigerar por debajo de 25ºC durante un período máximo de 5 días. |

Localization judge: **zero_shot** better. Both are accurate and reuse the only applicable TM wording (jeringa precargada, conservar), but B's 'sin refrigeración' is closer to the source 'un-refrigerated' and the reference, while A's 'fuera de la nevera' is more colloquial.  
Generic judge: **zero_shot** better. Both translations are accurate and keep the 25 °C limit and the single 5-day maximum, but B's 'sin refrigeración' is the more standard regulatory wording and closer to 'un-refrigerated', while A's 'fuera de la nevera' is more colloquial.

### Where RAG lost 2

**New segment:** uncommon: depression, disorientation, anxiety, insomnia, sleep disorder, abnormal dream

**Best fuzzy match (47% → a CAT tool shows nothing):** disorder (incl. hypersexuality, libido increased), Insomnia, Sleep disorder, Abnormal dreams

**Semantic match (similarity 83, judged reusable: partial):**  
EN: Uncommon: delirium, psychotic disorder, suicidal ideation, suicide attempt, thought blocking, abnormal dreams  
ES: Poco frecuentes: delirio, trastornos psicóticos, ideas suicidas, intentos de suicidio, bloqueo del pensamiento, sueños anormales

| | translation |
|---|---|
| zero-shot (today) | Poco frecuentes: depresión, desorientación, ansiedad, insomnio, trastorno del sueño, sueños anormales |
| **semantic RAG** | Poco frecuentes: depresión, desorientación, ansiedad, insomnio, trastorno del sueño, sueños anómalos |
| human reference | poco frecuentes: depresión, desorientación, ansiedad, insomnio, trastornos del sueño, sueños anormales |

Localization judge: **zero_shot** better. Both are accurate, but B reuses the approved TM term 'sueños anormales' while A replaces it with the unapproved 'sueños anómalos'.  
Generic judge: **zero_shot** better. Both translations are accurate and identical except for the last term; B's 'sueños anormales' matches the standard EU Spanish MedDRA term for 'abnormal dream', whereas A's 'sueños anómalos' is correct in meaning but less conventional.

### Where RAG lost 3

**New segment:** If pregnancy occurs during treatment, tell your doctor immediately.

**Best fuzzy match (54% → a CAT tool shows nothing):** If this happens to you, tell your doctor.

**Semantic match (similarity 84, judged reusable: partial):**  
EN: If you become pregnant during this time, despite the use of contraceptive measures, you should tell your doctor immediately.  
ES: Debe informar a su médico inmediatamente si se queda embarazada durante este tiempo, a pesar de utilizar medidas anticonceptivas.

| | translation |
|---|---|
| zero-shot (today) | Si queda embarazada durante el tratamiento, informe inmediatamente a su médico. |
| **semantic RAG** | Si se produce un embarazo durante el tratamiento, comunique a su médico inmediatamente. |
| human reference | Si se produjera un embarazo durante el tratamiento, informe a su médico inmediatamente. |

Localization judge: **zero_shot** better. Both are accurate, but A reuses the approved TM wording ('queda embarazada', 'informe... a su médico', 'inmediatamente'), whereas B swaps in 'comunique' for the approved 'informar' and also moves 'inmediatamente' to the end, diverging from the approved phrasing.  
Generic judge: **rag** better. Both convey the meaning, but B keeps the impersonal 'se produce un embarazo' of the source and reference, while A's 'si queda embarazada' narrows the condition to the patient; B's 'comunique a su médico' is slightly less idiomatic than 'informe', but it is still acceptable.

### Risk: negated segment, RAG output inaccurate 1

**New segment:** Press the pump onto the top of the bottle, and turn it anticlockwise until it clicks tightly into place.

**Best fuzzy match (95% → a CAT tool shows nothing):** Press the pump onto the top of the bottle, and turn it clockwise until it clicks tightly into place.

**Semantic match (similarity 99, judged reusable: partial):**  
EN: Press the pump onto the top of the bottle, and turn it clockwise until it clicks tightly into place.  
ES: Ajuste la bomba con la boca del frasco y enrosque con fuerza en el sentido de las agujas del reloj hasta que haga clic y ajuste perfectamente.

| | translation |
|---|---|
| zero-shot (today) | Presione la bomba en la parte superior del frasco y gírela en sentido antihorario hasta que encaje firmemente en su lugar con un clic. |
| **semantic RAG** | Ajuste la bomba con la boca del frasco y enrosque suavemente en el sentido contrario a las agujas del reloj hasta que haga clic y ajuste perfectamente. |

Localization judge: **zero_shot** better. A reuses the approved phrasing but wrongly changes 'con fuerza' to 'suavemente', which contradicts the source's 'tightly', while B is accurate though it ignores the approved terminology, and accuracy outweighs consistency.  
Generic judge: **zero_shot** better. A drops the instruction to press the pump onto the top of the bottle and adds 'suavemente', which is not in the source, while B conveys the pressing, the anticlockwise turn and the firm click into place accurately, in natural regulatory style.

### Risk: negated segment, RAG output inaccurate 2

**New segment:** Acute renal failure has never been reported through post-marketing surveillance in patients receiving parecoxib (see section 4.8).

**Best fuzzy match (96% → a CAT tool shows nothing):** Acute renal failure has been reported through post-marketing surveillance in patients receiving parecoxib (see section 4.8).

**Semantic match (similarity 86, judged reusable: partial):**  
EN: Acute renal failure has been reported through post-marketing surveillance in patients receiving parecoxib (see section 4.8).  
ES: Durante la vigilancia posterior a la comercialización, se ha notificado insuficiencia renal aguda en pacientes tratados con parecoxib (ver sección 4.8).

| | translation |
|---|---|
| zero-shot (today) | No se ha notificado nunca insuficiencia renal aguda en la vigilancia poscomercialización en pacientes tratados con parecoxib (véase la sección 4.8). |
| **semantic RAG** | Durante la vigilancia posterior a la comercialización, no se ha notificado insuficiencia renal aguda en pacientes tratados con parecoxib (ver sección 4.8). |

Localization judge: **zero_shot** better. A preserves 'never' (nunca) from the new segment, while B reuses the TM wording but drops 'never', weakening the meaning, and accuracy outweighs consistency.  
Generic judge: **zero_shot** better. Both are accurate, but A keeps the 'never' of the source ('nunca') while B drops it, which slightly weakens the meaning; A also uses the standard EU Spanish wording 'véase la sección 4.8' and the usual term 'poscomercialización'.
