# Side-by-side examples

### Real segment win 1

**New segment:** Irbesartan Hydrochlorothiazide Winthrop 300 mg/ 12.5 mg tablets.

**Best fuzzy match (67% → a CAT tool shows nothing):** CoAprovel 150 mg/ 12.5 mg tablets.

**Semantic match (similarity 92, judged reusable: partial):**  
EN: Irbesartan Hydrochlorothiazide Winthrop 300 mg/ 25 mg film-coated tablets.  
ES: Irbesartan Hydrochlorothiazide Winthrop, 300 mg/ 25 mg, comprimidos recubiertos con película.

| | translation |
|---|---|
| zero-shot (today) | Irbesartán/Hidroclorotiazida Winthrop 300 mg/12,5 mg comprimidos. |
| **semantic RAG** | Irbesartan Hydrochlorothiazide Winthrop, 300 mg/ 12,5 mg, comprimidos. |
| human reference | Irbesartan Hydrochlorothiazide Winthrop, 300 mg/ 12,5 mg, comprimidos. |

Localization judge: **rag** better. The new segment says only 'tablets' (not film-coated), so both correctly omit 'recubiertos con película' and use 12,5; but A reuses the approved product name 'Irbesartan Hydrochlorothiazide Winthrop' and comma punctuation, while B alters the approved product name to 'Irbesartán/Hidroclorotiazida' and changes the format.  
Generic judge: **rag** better. A keeps the product name "Irbesartan Hydrochlorothiazide Winthrop" exactly as authorised, matching the reference, whereas B alters the proprietary name by translating it and inserting a slash (Irbesartán/Hidroclorotiazida), and also uses "12,5" without the reference's spacing, so it no longer reproduces the registered name.

### Real segment win 2

**New segment:** Unit dose blister packs of 56 x 1 tablets for delivery in hospitals are also available.

**Best fuzzy match (68% → a CAT tool shows nothing):** Unidose blister packs of 56 x 1 film-coated tablet for delivery in hospitals are also available.

**Semantic match (similarity 92, judged reusable: partial):**  
EN: Unidose blister packs of 56 x 1 film-coated tablet for delivery in hospitals are also available.  
ES: También se encuentran disponibles en envases de 56 x 1 comprimido recubierto con película que contienen blisters unidosis para su suministro en hospitales.

| | translation |
|---|---|
| zero-shot (today) | También están disponibles blísteres de dosis unitaria de 56 x 1 comprimidos para suministro hospitalario. |
| **semantic RAG** | También se encuentran disponibles en envases de 56 x 1 comprimidos que contienen blisters unidosis para su suministro en hospitales. |
| human reference | También se encuentra disponible en envases de 56 x 1 comprimidos para su suministro en hospitales. |

Localization judge: **rag** better. Both are accurate to the new segment, which lacks 'film-coated' so 'comprimidos' is correct, but A reuses the approved phrasing ('se encuentran disponibles en envases de 56 x 1... que contienen blisters unidosis para su suministro en hospitales') while B replaces it with different wording ('dosis unitaria', 'blísteres de', 'suministro hospitalario').  
Generic judge: **zero_shot** better. B faithfully renders 'unit dose blister packs of 56 x 1 tablets' as 'blísteres de dosis unitaria de 56 x 1 comprimidos' in correct regulatory style, whereas A adds 'que contienen' (packs containing blisters), which restructures the meaning, and has a plural/agreement mismatch with the omitted subject and the awkward 'blisters unidosis'.

### Real segment win 3

**New segment:** Powder: lactose, sorbitol, L-histidine hydrochloride, L-alanine, sodium chloride, potassium chloride, disodium phosphate, monopotassium phosphate, calcium chloride, magnesium sulphate.

**Best fuzzy match (64% → a CAT tool shows nothing):** Lactose Sorbitol E420 L-histidine hydrochloride L-alanine Sodium chloride Potassium chloride Disodium phosphate Monopotassium phosphate Calcium chloride Magnesium sulphate

**Semantic match (similarity 84, judged reusable: partial):**  
EN: Lactose Sorbitol E420 L-histidine hydrochloride L-alanine Sodium chloride Potassium chloride Disodium phosphate Monopotassium phosphate Calcium chloride Magnesium sulphate  
ES: Lactosa Sorbitol E420 Clorhidrato de L-histidina L-alanina Cloruro Sódico Cloruro Potásico Fosfato Disódico Fosfato Monopotásico Cloruro Cálcico Sulfato Magnésico

| | translation |
|---|---|
| zero-shot (today) | Polvo: lactosa, sorbitol, hidrocloruro de L-histidina, L-alanina, cloruro de sodio, cloruro de potasio, fosfato disódico, fosfato monopotásico, cloruro de calcio, sulfato de magnesio. |
| **semantic RAG** | Polvo: lactosa, sorbitol, clorhidrato de L-histidina, L-alanina, cloruro sódico, cloruro potásico, fosfato disódico, fosfato monopotásico, cloruro cálcico, sulfato magnésico. |
| human reference | Lactosa, sorbitol, clorhidrato de L-histidina, L-alanina, cloruro sódico, cloruro potásico, fosfato disódico, fosfato monopotásico, cloruro cálcico, sulfato magnésico. |

Localization judge: **rag** better. Both translations are accurate to the new segment, including the "Powder:" label, but B reuses the approved TM terms (clorhidrato de L-histidina, cloruro sódico/potásico/cálcico, sulfato magnésico), while A substitutes different wording (hidrocloruro, cloruro de sodio/potasio/calcio, sulfato de magnesio).  
Generic judge: **rag** better. Both translations are accurate and complete, but B uses the standard Spanish regulatory/pharmacopoeial terms (clorhidrato, cloruro sódico/potásico/cálcico, sulfato magnésico) matching EU Spanish SmPC style, whereas A uses the less standard 'hidrocloruro' and the 'cloruro de X' forms.

### Real segment win 4

**New segment:** It is not known whether oseltamivir or the active metabolite are excreted in human milk.

**Best fuzzy match (69% → a CAT tool shows nothing):** Lactation It is not known whether azacitidine or its metabolites are excreted in human milk.

**Semantic match (similarity 83, judged reusable: partial):**  
EN: It is not known whether this medicinal products or its metabolites are excreted in human milk.  
ES: Se desconoce si este fármaco o sus metabolitos se excretan en la leche humana.

| | translation |
|---|---|
| zero-shot (today) | No se sabe si el oseltamivir o el metabolito activo se excretan en la leche materna. |
| **semantic RAG** | Se desconoce si oseltamivir o el metabolito activo se excretan en la leche humana. |
| human reference | Se desconoce si oseltamivir o el metabolito activo se excretan en la leche humana. |

Localization judge: **rag** better. Both are accurate, but A reuses the approved TM phrasing ('Se desconoce si... se excretan en la leche humana'), while B replaces it with 'No se sabe si' and 'leche materna', which departs from the approved wording.  
Generic judge: **rag** better. Both translations are accurate, but A uses the standard EU SmPC phrasing "Se desconoce si... leche humana" (matching the source's "human milk" and the reference), while B's "No se sabe" is less formal and "leche materna" is a slight deviation from "human milk".

### Real segment win 5

**New segment:** Each tablet contains: irbesartan 300 mg and hydrochlorothiazide 25 mg

**Best fuzzy match (69% → a CAT tool shows nothing):** Each tablet contains: irbesartan 150 mg and hydrochlorothiazide 12.5 mg

**Semantic match (similarity 96, judged reusable: partial):**  
EN: Each tablet contains: irbesartan 150 mg and hydrochlorothiazide 12.5 mg  
ES: Cada comprimido contiene: irbesartan 150 mg e hidroclorotiazida 12,5 mg

| | translation |
|---|---|
| zero-shot (today) | Cada comprimido contiene: 300 mg de irbesartán y 25 mg de hidroclorotiazida |
| **semantic RAG** | Cada comprimido contiene: irbesartan 300 mg e hidroclorotiazida 25 mg |
| human reference | Cada comprimido contiene: irbesartan 300 mg e hidroclorotiazida 25 mg |

Localization judge: **rag** better. Both translations are accurate to the new doses (300 mg and 25 mg), but B reuses the approved TM structure and terminology ("irbesartan 300 mg e hidroclorotiazida 25 mg"), while A restructures the phrasing to "300 mg de irbesartán y 25 mg de hidroclorotiazida" and changes the approved spelling "irbesartan" to "irbesartán".  
Generic judge: **tie** better. Both translations convey the same substances and doses with nothing added or lost; A uses the Spanish INN 'irbesartán' with a natural 'X mg de Y' structure, while B copies the reference's EU QRD-style format ('irbesartan 300 mg e hidroclorotiazida 25 mg'), which is the established SmPC convention, so neither is clearly better.

### Real segment win 6

**New segment:** Infections and infestations Rare: upper respiratory tract infection

**Best fuzzy match (33% → a CAT tool shows nothing):** Infections and infestations Uncommon Psychiatric disorders

**Semantic match (similarity 82, judged reusable: partial):**  
EN: Infections and infestations Uncommon (≥ 1/ 1000 to < 1/ 100): infection (primarily colds and upper respiratory tract infections)  
ES: Infecciones e infestaciones Poco Frecuentes (≥ 1/ 1000, < 1/ 100): infección (principalmente resfriados e infecciones del tracto respiratorio superior)

| | translation |
|---|---|
| zero-shot (today) | Infecciones e infestaciones Raras: infección de las vías respiratorias superiores |
| **semantic RAG** | Infecciones e infestaciones Raras: infección del tracto respiratorio superior |
| human reference | Infecciones e infestaciones Raras: infección del tracto respiratorio superior |

Localization judge: **rag** better. Both are accurate, but A reuses the approved TM phrasing 'infección del tracto respiratorio superior' and the 'Raras' frequency label, while B replaces the approved 'tracto respiratorio superior' with 'vías respiratorias superiores'.  
Generic judge: **tie** better. Both translations are accurate and use correct MedDRA-style terminology and regulatory style; 'infección del tracto respiratorio superior' (A) matches the reference exactly, while 'infección de las vías respiratorias superiores' (B) is an equally valid, widely used variant.

### Reworded TM entry (paraphrase) win 1

**New segment:** Patients who take opioids like fentanyl over and over can become tolerant and physically or psychologically dependent.

**Best fuzzy match (20% → a CAT tool shows nothing):** Patients who take Humira must be given the special alert card that summarises the safety information about the medicine.

**Semantic match (similarity 88, judged reusable: partial):**  
EN: Upon repeated administration of opioids such as fentanyl, tolerance and physical and/ or psychological dependence may develop.  
ES: La administración repetida de opioides como fentanilo, puede producir tolerancia y dependencia física y/ o fisiológica.

| | translation |
|---|---|
| zero-shot (today) | Los pacientes que toman opioides como fentanilo de forma repetida pueden volverse tolerantes y dependientes física o psicológicamente. |
| **semantic RAG** | Los pacientes que toman opioides como fentanilo repetidamente pueden desarrollar tolerancia y dependencia física o psicológica. |

Localization judge: **rag** better. Both are accurate, but A reuses the approved noun phrasing 'tolerancia y dependencia física o psicológica' (correctly avoiding the TM's 'fisiológica' error), while B rewrites it as adjectives/adverbs ('tolerantes y dependientes física o psicológicamente') instead of the approved wording.  
Generic judge: **rag** better. Both translations convey the meaning accurately, but A uses the standard regulatory wording 'desarrollar tolerancia y dependencia física o psicológica', which is more concise and natural than B's 'volverse tolerantes y dependientes física o psicológicamente'.

### Reworded TM entry (restructure) win 2

**New segment:** Tolerance and physical and/or psychological dependence may develop when opioids such as fentanyl are given repeatedly.

**Best fuzzy match (32% → a CAT tool shows nothing):** Tolerance, physical or psychological dependence may develop if you use Fentanyl-ratiopharm for a longer period.

**Semantic match (similarity 95, judged reusable: partial):**  
EN: Upon repeated administration of opioids such as fentanyl, tolerance and physical and/ or psychological dependence may develop.  
ES: La administración repetida de opioides como fentanilo, puede producir tolerancia y dependencia física y/ o fisiológica.

| | translation |
|---|---|
| zero-shot (today) | La tolerancia y la dependencia física y/o psicológica pueden desarrollarse cuando se administran repetidamente opioides como el fentanilo. |
| **semantic RAG** | La administración repetida de opioides como fentanilo puede producir tolerancia y dependencia física y/ o psicológica. |

Localization judge: **rag** better. Both correctly render 'psychological' as 'psicológica' (the TM's 'fisiológica' is an error), but A reuses the approved phrasing and structure ('La administración repetida de opioides como fentanilo... puede producir tolerancia y dependencia...') while B rewords it unnecessarily.  
Generic judge: **rag** better. Both translations are accurate, but A uses the concise, natural regulatory phrasing 'puede producir tolerancia y dependencia' (although it has a minor spacing error in 'y/ o'), whereas B follows the English structure more literally and sounds slightly less idiomatic in Spanish SmPC style.

### Reworded TM entry (restructure) win 3

**New segment:** Turn the pump clockwise after pressing it onto the top of the bottle, until it clicks tightly into place.

**Best fuzzy match (57% → a CAT tool shows nothing):** Press the pump onto the top of the bottle, and turn it clockwise until it clicks tightly into place.

**Semantic match (similarity 98, judged reusable: partial):**  
EN: Press the pump onto the top of the bottle, and turn it clockwise until it clicks tightly into place.  
ES: Ajuste la bomba con la boca del frasco y enrosque con fuerza en el sentido de las agujas del reloj hasta que haga clic y ajuste perfectamente.

| | translation |
|---|---|
| zero-shot (today) | Gire la bomba en el sentido de las agujas del reloj después de presionarla sobre la parte superior del frasco, hasta que encaje firmemente con un clic. |
| **semantic RAG** | Gire la bomba en el sentido de las agujas del reloj después de encajarla en la boca del frasco, hasta que haga clic y ajuste perfectamente. |

Localization judge: **rag** better. Both are accurate, but A reuses the approved TM terminology ('boca del frasco', 'hasta que haga clic y ajuste perfectamente') while B substitutes different wording ('parte superior del frasco', 'encaje firmemente con un clic').  
Generic judge: **zero_shot** better. B faithfully renders "pressing it onto the top of the bottle" (presionarla sobre la parte superior del frasco) and "clicks tightly into place" (encaje firmemente con un clic), whereas A changes "pressing" to "encajarla" and "top of the bottle" to "boca del frasco", and its "hasta que haga clic y ajuste perfectamente" is less natural and slightly alters the meaning.

### Where RAG lost 1

**New segment:** The bottles contain desiccant canisters that should remain in the container.

**Best fuzzy match (33% → a CAT tool shows nothing):** Desiccant should not be removed from the container.

**Semantic match (similarity 81, judged reusable: partial):**  
EN: Desiccant should not be removed from the container.  
ES: El desecante no se debe sacar del envase.

| | translation |
|---|---|
| zero-shot (today) | Los frascos contienen cartuchos desecantes que deben permanecer en el envase. |
| **semantic RAG** | Las botellas contienen canisters de desecante que deben permanecer en el envase. |
| human reference | Los envases contienen una bolsa desecante que debe permanecer dentro del frasco. |

Localization judge: **zero_shot** better. Both translations convey the meaning, but A renders 'canisters' in natural Spanish ('cartuchos desecantes') and reuses the approved 'envase' for 'container', whereas B leaves 'canisters' untranslated and uses the approved 'desecante' only in a partly English phrase, making it less consistent and less polished.  
Generic judge: **zero_shot** better. A renders 'bottles' as 'frascos' (the standard pharmaceutical term) and 'desiccant canisters' as 'cartuchos desecantes', which is acceptable and conveys the instruction that they stay in the container, whereas B uses the less suitable 'botellas' and leaves 'canisters' untranslated, an unnatural anglicism in regulatory Spanish.

### Where RAG lost 2

**New segment:** The dosage may be titrated upward until blood pressure is controlled or to a maximum of 40 mg daily.

**Best fuzzy match (33% → a CAT tool shows nothing):** The dose can be raised by your doctor gradually, and if needed, even up to a maximum dose of 375 mg daily for depression.

**Semantic match (similarity 87, judged reusable: none):**  
EN: The dose may later be increased to 300 mg (four tablets a day) once daily depending on blood pressure response.  
ES: Posteriormente, y dependiendo de la respuesta de la presión arterial, esta dosis puede aumentarse a 300 mg una vez al día (cuatro comprimidos al día).

| | translation |
|---|---|
| zero-shot (today) | La dosis puede ajustarse gradualmente al alza hasta que se controle la presión arterial o hasta una dosis máxima de 40 mg al día. |
| **semantic RAG** | La dosis puede incrementarse hasta que la presión arterial esté controlada o hasta un máximo de 40 mg al día. |
| human reference | La dosis podrá ajustarse al alza hasta conseguir el control de la presión arterial o hasta un máximo de 40 mg al día. |

Localization judge: **zero_shot** better. Both are accurate and reuse approved terms like 'dosis', 'presión arterial' and 'al día', but A better conveys 'titrated' with 'ajustarse gradualmente al alza', while B's 'incrementarse' loses the titration nuance and departs from the approved 'aumentarse' without a gain in precision.  
Generic judge: **zero_shot** better. Both are accurate with the 40 mg daily maximum and the blood-pressure-control condition preserved, but A's "ajustarse ... al alza" mirrors the reference and the standard term "titrated upward", whereas B's "incrementarse" is less precise as it loses the titration nuance, and A's "gradualmente" is a minor, acceptable implication of titration.

### Where RAG lost 3

**New segment:** uncommon: depression, disorientation, anxiety, insomnia, sleep disorder, abnormal dream

**Best fuzzy match (47% → a CAT tool shows nothing):** disorder (incl. hypersexuality, libido increased), Insomnia, Sleep disorder, Abnormal dreams

**Semantic match (similarity 83, judged reusable: partial):**  
EN: Uncommon: delirium, psychotic disorder, suicidal ideation, suicide attempt, thought blocking, abnormal dreams  
ES: Poco frecuentes: delirio, trastornos psicóticos, ideas suicidas, intentos de suicidio, bloqueo del pensamiento, sueños anormales

| | translation |
|---|---|
| zero-shot (today) | poco frecuentes: depresión, desorientación, ansiedad, insomnio, trastorno del sueño, sueños anormales |
| **semantic RAG** | Poco frecuentes: depresión, desorientación, ansiedad, insomnio, alteraciones del sueño, sueños anómalos |
| human reference | poco frecuentes: depresión, desorientación, ansiedad, insomnio, trastornos del sueño, sueños anormales |

Localization judge: **zero_shot** better. Both translations are accurate, but B reuses the approved terms "trastorno" and "sueños anormales", while A replaces them with "alteraciones" and "anómalos", which are not in the TM.  
Generic judge: **zero_shot** better. Both are accurate, but B follows the reference more closely with the standard MedDRA-style terms 'trastorno del sueño' and 'sueños anormales' and keeps the lowercase 'poco frecuentes' of the source, whereas A uses 'alteraciones del sueño' and 'sueños anómalos', which are correct but less standard.

### Risk: negated segment, RAG output inaccurate 1

**New segment:** Herceptin treatment can be initiated by any physician, even one not experienced in the administration of cytotoxic chemotherapy (see 4.4).

**Best fuzzy match (73% → a CAT tool shows nothing):** Herceptin treatment should only be initiated by a physician experienced in the administration of cytotoxic chemotherapy (see 4.4).

**Semantic match (similarity 85, judged reusable: partial):**  
EN: Herceptin treatment should only be initiated by a physician experienced in the administration of cytotoxic chemotherapy (see 4.4).  
ES: El tratamiento con Herceptin únicamente debe iniciarse por un especialista con experiencia en la administración de quimioterapia citotóxica (Ver 4.4).

| | translation |
|---|---|
| zero-shot (today) | El tratamiento con Herceptin puede ser iniciado por cualquier médico, incluso por uno sin experiencia en la administración de quimioterapia citotóxica (véase 4.4). |
| **semantic RAG** | El tratamiento con Herceptin puede iniciarse por cualquier especialista, incluso uno sin experiencia en la administración de quimioterapia citotóxica (Ver 4.4). |

Localization judge: **zero_shot** better. A correctly renders 'any physician' as 'cualquier médico', while B reuses the TM's 'especialista' and so narrows the meaning to specialists, and accuracy outweighs terminology consistency.  
Generic judge: **zero_shot** better. Both convey the meaning, but B changes "physician" to "especialista" (specialist), which narrows the meaning, and uses "Ver 4.4" instead of the standard EU style "véase 4.4", while A uses "médico" and "véase" correctly.
