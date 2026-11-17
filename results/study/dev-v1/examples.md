# Examples: largest QE changes vs zero-shot

Selected by CometKiwi Δ. QE is a model estimate; these are pointers for manual inspection, not verdicts.

## hybrid_ctx: Degradations

### Ka43608cada29:es (KDE4/es, band 75-84, fuzzy 80) ΔKiwi -0.166

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** Geométrico - Flecha izquierda con muesca
- **hybrid_ctx:** Geometría - Flecha izquierda irregular
- **Reference (not shown to any system or evaluator):** Geometría - Flecha izquierda irregularStencils
- TM [partial]: Geometric - Notched Right Arrow → Geometría - Flecha derecha irregularStencils
- TM [terminology]: Geometric - Left-Right Arrow → Geometría - Flecha izquierda-derechaStencils
- TM [terminology]: Geometric - Up Arrow → Geometría - Flecha arribaStencils

### Kfb4f23faf64d:es (KDE4/es, band 50-74, fuzzy 50) ΔKiwi -0.164

- **Source:** Delete Sieve Script Confirmation
- **Zero-shot:** Confirmación de eliminación del script Sieve
- **hybrid_ctx:** Confirmación para eliminar el guión de Sieve
- **Reference (not shown to any system or evaluator):** Conformación de borrado de guión de Sieve
- TM [terminology]: The Sieve script was successfully uploaded. → El guión de Sieve se publicó correctamente.
- TM [partial]: Undo File Copy Confirmation → Confirmación para deshacer la copia de archivo
- TM [misleading]: Delete permanently without confirmation → Eliminar permanentemente sin confirmación

### K0819f3f5afd7:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 75) ΔKiwi -0.163

- **Source:** & Copy Folders To
- **Zero-shot:** &复制文件夹到
- **hybrid_ctx:** 文件夹复制至( C)
- **Reference (not shown to any system or evaluator):** 文件夹复制至( C)
- TM [full]: & Copy Folder To → 文件夹复制至( C)
- TM [partial]: & Move Folder To → 文件夹移至( M)
- TM [terminology]: & Add Folder to Top → 增加文件夹到顶端( A)

### Ke4a42dc6389d:es (KDE4/es, band 85-94, fuzzy 86) ΔKiwi -0.158

- **Source:** Use this button to record this transaction
- **Zero-shot:** Use este botón para registrar esta transacción
- **hybrid_ctx:** Use este botón para registrar este asiento
- **Reference (not shown to any system or evaluator):** Use este botón para ingresar este asiento
- TM [partial]: Use this button to skip this transaction → Use este botón para saltear este asiento
- TM [partial]: Use this button to show the generated report information about this crash. → Use este botón para mostrar la información del reporte generada de este fallo. @info/ plain
- TM [terminology]: Click this button to accept the invitation. → Pulse este botón para aceptar la invitación. @action: button

### E9c3c6005a3ff:es (EMEA/es, band 85-94, fuzzy 93) ΔKiwi -0.153

- **Source:** Route of Administration Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use
- **Zero-shot:** Vía de administración Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral
- **hybrid_ctx:** Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral
- **Reference (not shown to any system or evaluator):** Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral
- TM [partial]: Route of Administration Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use → Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral
- TM [partial]: Route of Administration Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use → Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral
- TM [misleading]: Route of Administration Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Intravenous Use → Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía intravenosa

### Ka43608cada29:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 80) ΔKiwi -0.146

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** 几何 - 左向缺口箭头
- **hybrid_ctx:** 几何 - 有锯齿的左箭头Stencils
- **Reference (not shown to any system or evaluator):** 几何 - 带锯齿的左箭头Stencils
- TM [partial]: Geometric - Notched Right Arrow → 几何 - 有锯齿的右箭头Stencils
- TM [terminology]: Geometric - Left-Right Arrow → 几何 - 左右箭头Stencils
- TM [terminology]: Geometric - Up Arrow → 几何 - 上箭头Stencils

## hybrid_ctx: Improvements

### Ef33912f6d25b:es (EMEA/es, band 75-84, fuzzy 80) ΔKiwi +0.316

- **Source:** BEFORE YOU ARE GIVEN Optimark
- **Zero-shot:** ANTES DE QUE SE LE ADMINISTRE Optimark
- **hybrid_ctx:** ANTES DE RECIBIR Optimark
- **Reference (not shown to any system or evaluator):** ANTES DE QUE SE LE ADMINISTRE Optimark
- TM [partial]: BEFORE YOU ARE GIVEN GEMZAR → ANTES DE USAR GEMZAR
- TM [partial]: BEFORE YOU ARE GIVEN SIMULECT → ANTES DE RECIBIR SIMULECT
- TM [partial]: BEFORE YOU ARE GIVEN YONDELIS → ANTES DE USAR YONDELIS

### Ka43608cada29:de (KDE4/de, band 75-84, fuzzy 80) ΔKiwi +0.173

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** Geometrisch - Einkerbung Pfeil links
- **hybrid_ctx:** Geometrie - Eingekerbter Pfeil nach links
- **Reference (not shown to any system or evaluator):** Geometrie - Eingekerbter Pfeil nach linksStencils
- TM [partial]: Geometric - Notched Right Arrow → Geometrie - Eingekerbter Pfeil nach rechtsStencils
- TM [terminology]: Geometric - Left-Right Arrow → Geometrie - Pfeil nach links und rechtsStencils
- TM [partial]: Geometric - Up Arrow → Geometrie - Pfeil nach obenStencils

### Ka4ac2084f554:es (KDE4/es, band 85-94, fuzzy 90) ΔKiwi +0.167

- **Source:** The value the zoom-out tool should use.
- **Zero-shot:** El valor que debe usar la herramienta de alejar.
- **hybrid_ctx:** El valor que la herramienta de alejamiento debería usar
- **Reference (not shown to any system or evaluator):** El valor de alejamiento que la herramienta debería usar.
- TM [full]: The value the zoom-out tool should use → El valor que la herramienta de alejamiento debería usar
- TM [partial]: The value the zoom-in tool should use → El valor que la herramienta de aumento debería usar
- TM [none]: Select the zoom factor. → Seleccione el factor de ampliación.

### Ea238aebc5300:es (EMEA/es, band 75-84, fuzzy 82) ΔKiwi +0.072

- **Source:** The grounds for referral were submitted on 10 February 1997 and are appended to this opinion.
- **Zero-shot:** Los motivos del procedimiento de consulta se presentaron el 10 de febrero de 1997 y se adjuntan a la presente dictamen.
- **hybrid_ctx:** Los fundamentos de la remisión fueron enviados el 10 de febrero de 1997 y se adjuntan a este dictamen.
- **Reference (not shown to any system or evaluator):** El fundamento de la remisión se presentó ante la EMEA el 10 de febrero de 1997 y se adjunta a este dictamen.
- TM [full]: The grounds for referral were submitted on 12 October 1998 and are appended to this opinion. → Los fundamentos de la remisión fueron enviados el 12 de octubre de 1998 y se adjuntan a este dictamen.
- TM [terminology]: The marketing authorisation was renewed on 10 February 2002 and on 10 February 2007. → La autorización de comercialización fue renovada el 10 de febrero de 2002 y el 10 de febrero de 2007.
- TM [misleading]: The grounds for appeal were jointly lodged by the marketing authorisation holders on 11 August 1995. → Las razones alegadas para el recurso fueron presentadas conjuntamente por los titulares de la autorización de comercialización el día 11 de agosto de 1995.

### Ka634ad575582:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 75) ΔKiwi +0.067

- **Source:** Mail Conduit for KPilot
- **Zero-shot:** KPilot 的邮件传输代理
- **hybrid_ctx:** KPilot 的 Mail 管道
- **Reference (not shown to any system or evaluator):** KPilot 的 Mail 管道
- TM [partial]: Keyring Conduit for KPilot → KPilot 的密钥串管道
- TM [partial]: Configures the Mail Conduit for KPilot → 配置 KPilot 的 Mail 管道
- TM [partial]: Memofile Conduit for KPilot → KPilot 的备忘录管道

### E44d806f4707a:es (EMEA/es, band 50-74, fuzzy 50) ΔKiwi +0.064

- **Source:** FIRMAGON 80 mg powder for injection degarelix SC use only
- **Zero-shot:** FIRMAGON 80 mg polvo para solución para inyección degarelix solo para uso SC
- **hybrid_ctx:** FIRMAGON 80 mg polvo para inyección degarelix solo para uso subcutáneo
- **Reference (not shown to any system or evaluator):** FIRMAGON 80 mg polvo para inyectable Degarelix Sólo para vía SC
- TM [partial]: PegIntron 80 micrograms powder for injection SC → PegIntron 80 microgramos polvo para solución inyectable Vía subcutánea
- TM [partial]: FIRMAGON 80 mg powder and solvent for solution for injection → FIRMAGON 80 mg polvo y disolvente para solución inyectable
- TM [partial]: Enbrel 25 mg powder for injection etanercept Subcutaneous use → Enbrel 25 mg polvo para inyección Etanercept Vía subcutánea.

## structured_ctx: Degradations

### K0819f3f5afd7:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 75) ΔKiwi -0.186

- **Source:** & Copy Folders To
- **Zero-shot:** &复制文件夹到
- **structured_ctx:** 文件夹复制至(C)
- **Reference (not shown to any system or evaluator):** 文件夹复制至( C)
- TM [full]: & Copy Folder To → 文件夹复制至( C)
- TM [partial]: & Move Folder To → 文件夹移至( M)
- TM [terminology]: & Add Folder to Top → 增加文件夹到顶端( A)

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "Folder" → "文件夹"

Phrasing in previous translations:
- "Copy Folder To" → "文件夹复制至"

Simplified Chinese conventions seen in previous translations:
- The ampersand (&) in the source indicates a keyboard shortcut, which is translated as a letter in parentheses at the end of the Chinese string.

Differences from the historical segments (do not carry these over):
- Historical segment uses singular 'Folder'; new segment uses plural 'Folders'.
```

### Ka43608cada29:es (KDE4/es, band 75-84, fuzzy 80) ΔKiwi -0.166

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** Geométrico - Flecha izquierda con muesca
- **structured_ctx:** Geometría - Flecha izquierda irregular
- **Reference (not shown to any system or evaluator):** Geometría - Flecha izquierda irregularStencils
- TM [partial]: Geometric - Notched Right Arrow → Geometría - Flecha derecha irregularStencils
- TM [terminology]: Geometric - Left-Right Arrow → Geometría - Flecha izquierda-derechaStencils
- TM [terminology]: Geometric - Up Arrow → Geometría - Flecha arribaStencils

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "Geometric" → "Geometría"
- "Left" → "izquierda"
- "Arrow" → "Flecha"

Spanish conventions seen in previous translations:
- Use 'Geometría -' as the prefix for Geometric categories.

Differences from the historical segments (do not carry these over):
- Historical segment refers to 'Right Arrow'; new segment refers to 'Left Arrow'.
- Historical segment uses 'irregular' for 'Notched'; translator should verify if 'irregular' is the intended term for 'Notched' in the new segment.
```

### Kfb4f23faf64d:es (KDE4/es, band 50-74, fuzzy 50) ΔKiwi -0.164

- **Source:** Delete Sieve Script Confirmation
- **Zero-shot:** Confirmación de eliminación del script Sieve
- **structured_ctx:** Confirmación de eliminación del guión de Sieve
- **Reference (not shown to any system or evaluator):** Conformación de borrado de guión de Sieve
- TM [terminology]: The Sieve script was successfully uploaded. → El guión de Sieve se publicó correctamente.
- TM [partial]: Undo File Copy Confirmation → Confirmación para deshacer la copia de archivo
- TM [misleading]: Delete permanently without confirmation → Eliminar permanentemente sin confirmación

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "Sieve script" → "guión de Sieve"
- "Confirmation" → "Confirmación"

Differences from the historical segments (do not carry these over):
- Historical segment refers to deleting 'permanently without confirmation'; new segment is a 'Confirmation' dialog for deletion.
```

### Ke4a42dc6389d:es (KDE4/es, band 85-94, fuzzy 86) ΔKiwi -0.158

- **Source:** Use this button to record this transaction
- **Zero-shot:** Use este botón para registrar esta transacción
- **structured_ctx:** Use este botón para registrar este asiento
- **Reference (not shown to any system or evaluator):** Use este botón para ingresar este asiento
- TM [partial]: Use this button to skip this transaction → Use este botón para saltear este asiento
- TM [partial]: Use this button to show the generated report information about this crash. → Use este botón para mostrar la información del reporte generada de este fallo. @info/ plain
- TM [terminology]: Click this button to accept the invitation. → Pulse este botón para aceptar la invitación. @action: button

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "this button" → "este botón"
- "transaction" → "asiento"

Phrasing in previous translations:
- "Use this button to" → "Use este botón para"

Spanish conventions seen in previous translations:
- Formal address (usted) used for instructions

Differences from the historical segments (do not carry these over):
- historical segment says 'skip'; new segment says 'record'
```

### K7213a5234c7a:de (KDE4/de, band 85-94, fuzzy 89) ΔKiwi -0.146

- **Source:** Assigning image tags. Please wait...
- **Zero-shot:** Bildtags werden zugewiesen. Bitte warten...
- **structured_ctx:** Stichwörter werden zugewiesen. Bitte warten...
- **Reference (not shown to any system or evaluator):** Das Stichwort wird den Bildern zugewiesen. Bitte warten...
- TM [partial]: Removing image tags. Please wait... → Das Stichwort wird entfernt. Bitte warten...
- TM [partial]: Revising Exif Orientation tags. Please wait... → Die Exif-Ausrichtung der Bilder wird bereinigt. Bitte warten...
- TM [none]: Searching for Images. Please Wait... → Bitten warten Sie, während die Suche nach Bildern läuft...

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "image tags" → "Stichwort"

Phrasing in previous translations:
- "Please wait..." → "Bitte warten..."

Differences from the historical segments (do not carry these over):
- historical segment says 'Removing'; new segment says 'Assigning'
```

### Kfb4f23faf64d:zh_CN (KDE4/zh_CN, band 50-74, fuzzy 50) ΔKiwi -0.135

- **Source:** Delete Sieve Script Confirmation
- **Zero-shot:** 删除 Sieve 脚本确认
- **structured_ctx:** 确认删除筛选脚本
- **Reference (not shown to any system or evaluator):** 删除筛选脚本确认
- TM [terminology]: The Sieve script was successfully uploaded. → 筛选脚本已成功上传 。
- TM [style_convention]: Undo File Copy Confirmation → 确认撤消文件复制
- TM [terminology]: Delete permanently without confirmation → 不经确认而永久删除

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "Sieve script" → "筛选脚本"
- "Confirmation" → "确认"
- "Delete" → "删除"

Simplified Chinese conventions seen in previous translations:
- Confirmation dialogs/actions are translated as '确认' + [action]

Differences from the historical segments (do not carry these over):
- Historical segment refers to deleting 'permanently without confirmation'; new segment is a confirmation for the deletion itself.
```

## structured_ctx: Improvements

### Ef33912f6d25b:es (EMEA/es, band 75-84, fuzzy 80) ΔKiwi +0.316

- **Source:** BEFORE YOU ARE GIVEN Optimark
- **Zero-shot:** ANTES DE QUE SE LE ADMINISTRE Optimark
- **structured_ctx:** ANTES DE RECIBIR Optimark
- **Reference (not shown to any system or evaluator):** ANTES DE QUE SE LE ADMINISTRE Optimark
- TM [partial]: BEFORE YOU ARE GIVEN GEMZAR → ANTES DE USAR GEMZAR
- TM [partial]: BEFORE YOU ARE GIVEN SIMULECT → ANTES DE RECIBIR SIMULECT
- TM [partial]: BEFORE YOU ARE GIVEN YONDELIS → ANTES DE USAR YONDELIS

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Phrasing in previous translations:
- "BEFORE YOU ARE GIVEN" → "ANTES DE USAR"
- "BEFORE YOU ARE GIVEN" → "ANTES DE RECIBIR"

Spanish conventions seen in previous translations:
- Use of uppercase for section headings

Differences from the historical segments (do not carry these over):
- historical segment refers to GEMZAR; new segment refers to Optimark
- historical segment refers to SIMULECT; new segment refers to Optimark
- historical segment refers to YONDELIS; new segment refers to Optimark
```

### Ka43608cada29:de (KDE4/de, band 75-84, fuzzy 80) ΔKiwi +0.241

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** Geometrisch - Einkerbung Pfeil links
- **structured_ctx:** Geometrie - Eingekerbter Pfeil links
- **Reference (not shown to any system or evaluator):** Geometrie - Eingekerbter Pfeil nach linksStencils
- TM [partial]: Geometric - Notched Right Arrow → Geometrie - Eingekerbter Pfeil nach rechtsStencils
- TM [terminology]: Geometric - Left-Right Arrow → Geometrie - Pfeil nach links und rechtsStencils
- TM [partial]: Geometric - Up Arrow → Geometrie - Pfeil nach obenStencils

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "Geometric" → "Geometrie"
- "Notched" → "Eingekerbter"
- "Arrow" → "Pfeil"

Differences from the historical segments (do not carry these over):
- historical segment says Right Arrow; new segment says Left Arrow
```

### Ka4ac2084f554:es (KDE4/es, band 85-94, fuzzy 90) ΔKiwi +0.174

- **Source:** The value the zoom-out tool should use.
- **Zero-shot:** El valor que debe usar la herramienta de alejar.
- **structured_ctx:** El valor que la herramienta de alejamiento debería usar.
- **Reference (not shown to any system or evaluator):** El valor de alejamiento que la herramienta debería usar.
- TM [full]: The value the zoom-out tool should use → El valor que la herramienta de alejamiento debería usar
- TM [partial]: The value the zoom-in tool should use → El valor que la herramienta de aumento debería usar
- TM [none]: Select the zoom factor. → Seleccione el factor de ampliación.

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "zoom-out tool" → "herramienta de alejamiento"
- "value" → "valor"

Phrasing in previous translations:
- "The value the zoom-out tool should use" → "El valor que la herramienta de alejamiento debería usar"

Differences from the historical segments (do not carry these over):
- Historical segment refers to 'zoom-in tool' (herramienta de aumento), whereas new segment refers to 'zoom-out tool'.
```

### Ka43608cada29:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 80) ΔKiwi +0.117

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** 几何 - 左向缺口箭头
- **structured_ctx:** 几何 - 有锯齿的左箭头
- **Reference (not shown to any system or evaluator):** 几何 - 带锯齿的左箭头Stencils
- TM [partial]: Geometric - Notched Right Arrow → 几何 - 有锯齿的右箭头Stencils
- TM [terminology]: Geometric - Left-Right Arrow → 几何 - 左右箭头Stencils
- TM [terminology]: Geometric - Up Arrow → 几何 - 上箭头Stencils

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "Geometric" → "几何"
- "Notched" → "有锯齿的"
- "Arrow" → "箭头"

Simplified Chinese conventions seen in previous translations:
- Use ' - ' as a separator between the category and the specific item.

Differences from the historical segments (do not carry these over):
- Historical segment refers to 'Right Arrow'; new segment refers to 'Left Arrow'.
```

### Ka634ad575582:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 75) ΔKiwi +0.073

- **Source:** Mail Conduit for KPilot
- **Zero-shot:** KPilot 的邮件传输代理
- **structured_ctx:** KPilot 的邮件管道
- **Reference (not shown to any system or evaluator):** KPilot 的 Mail 管道
- TM [partial]: Keyring Conduit for KPilot → KPilot 的密钥串管道
- TM [partial]: Configures the Mail Conduit for KPilot → 配置 KPilot 的 Mail 管道
- TM [partial]: Memofile Conduit for KPilot → KPilot 的备忘录管道

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "Conduit" → "管道"
- "KPilot" → "KPilot"

Simplified Chinese conventions seen in previous translations:
- Use the structure '[Product] 的 [Component] 管道' for conduit naming.

Differences from the historical segments (do not carry these over):
- Historical segment refers to 'Keyring'; new segment refers to 'Mail'.
- Historical segment refers to 'Memofile'; new segment refers to 'Mail'.
```

### Ea238aebc5300:es (EMEA/es, band 75-84, fuzzy 82) ΔKiwi +0.072

- **Source:** The grounds for referral were submitted on 10 February 1997 and are appended to this opinion.
- **Zero-shot:** Los motivos del procedimiento de consulta se presentaron el 10 de febrero de 1997 y se adjuntan a la presente dictamen.
- **structured_ctx:** Los fundamentos de la remisión fueron enviados el 10 de febrero de 1997 y se adjuntan a este dictamen.
- **Reference (not shown to any system or evaluator):** El fundamento de la remisión se presentó ante la EMEA el 10 de febrero de 1997 y se adjunta a este dictamen.
- TM [full]: The grounds for referral were submitted on 12 October 1998 and are appended to this opinion. → Los fundamentos de la remisión fueron enviados el 12 de octubre de 1998 y se adjuntan a este dictamen.
- TM [terminology]: The marketing authorisation was renewed on 10 February 2002 and on 10 February 2007. → La autorización de comercialización fue renovada el 10 de febrero de 2002 y el 10 de febrero de 2007.
- TM [misleading]: The grounds for appeal were jointly lodged by the marketing authorisation holders on 11 August 1995. → Las razones alegadas para el recurso fueron presentadas conjuntamente por los titulares de la autorización de comercialización el día 11 de agosto de 1995.

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "grounds for referral" → "fundamentos de la remisión"
- "opinion" → "dictamen"

Phrasing in previous translations:
- "were submitted on" → "fueron enviados el"
- "are appended to this opinion" → "se adjuntan a este dictamen"

Spanish conventions seen in previous translations:
- Date format: [day] de [month] de [year]

Differences from the historical segments (do not carry these over):
- Historical segment date is 12 October 1998; new segment date is 10 February 1997.
```

## draft_ctx: Degradations

### Ka43608cada29:es (KDE4/es, band 75-84, fuzzy 80) ΔKiwi -0.293

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** Geométrico - Flecha izquierda con muesca
- **draft_ctx:** Geometría - Flecha izquierda irregularStencils
- **Reference (not shown to any system or evaluator):** Geometría - Flecha izquierda irregularStencils
- TM [partial]: Geometric - Notched Right Arrow → Geometría - Flecha derecha irregularStencils
- TM [terminology]: Geometric - Left-Right Arrow → Geometría - Flecha izquierda-derechaStencils
- TM [terminology]: Geometric - Up Arrow → Geometría - Flecha arribaStencils

### Kd2585fdc51e4:de (KDE4/de, band 75-84, fuzzy 75) ΔKiwi -0.242

- **Source:** Santa Cruz del Quiché
- **Zero-shot:** Santa Cruz del Quiché
- **draft_ctx:** Santa Cruz del Quichéguatemala.kgm
- **Reference (not shown to any system or evaluator):** Santa Cruz del Quichéguatemala.kgm
- TM [terminology]: Santa Cruz de Tenerife → Santa Cruz de Tenerifespain_provinces.kgm
- TM [partial]: Santa Cruz del Seibo → Santa Cruz del Seibodominican_republic.kgm
- TM [terminology]: Santa Cruz de la Palma → Santa Cruz de la PalmaCity in Tenerife Spain

### E68521922e4c5:es (EMEA/es, band 100, fuzzy 100) ΔKiwi -0.195

- **Source:** uth solution for injection, to distribute under the skin, then remove.
- **Zero-shot:** solución inyectable, para administrar por vía subcutánea y posteriormente retirar.
- **draft_ctx:** solución inyectable, para distribuir bajo la piel, después extraiga la aguja.
- **Reference (not shown to any system or evaluator):** an permitir que Viraferon, solución inyectable, se distribuya bajo la piel, después extraiga la aguja.
- TM [full]: uth solution for injection, to distribute under the skin, then remove. → an permitir que Viraferon, soluc ión inyectable, se distribuya bajo la piel, después extraiga la aguja.
- TM [misleading]: Ultratard is for injection under the skin (subcutaneously). → directamente en una vena o músculo.
- TM [terminology]: Protaphane is for injection under the skin (subcutaneously). → Protaphane se inyecta bajo la piel (administración subcutánea).

### Kfb4f23faf64d:es (KDE4/es, band 50-74, fuzzy 50) ΔKiwi -0.164

- **Source:** Delete Sieve Script Confirmation
- **Zero-shot:** Confirmación de eliminación del script Sieve
- **draft_ctx:** Confirmación para eliminar el guión de Sieve
- **Reference (not shown to any system or evaluator):** Conformación de borrado de guión de Sieve
- TM [terminology]: The Sieve script was successfully uploaded. → El guión de Sieve se publicó correctamente.
- TM [partial]: Undo File Copy Confirmation → Confirmación para deshacer la copia de archivo
- TM [misleading]: Delete permanently without confirmation → Eliminar permanentemente sin confirmación

### K0819f3f5afd7:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 75) ΔKiwi -0.163

- **Source:** & Copy Folders To
- **Zero-shot:** &复制文件夹到
- **draft_ctx:** 文件夹复制至( C)
- **Reference (not shown to any system or evaluator):** 文件夹复制至( C)
- TM [full]: & Copy Folder To → 文件夹复制至( C)
- TM [partial]: & Move Folder To → 文件夹移至( M)
- TM [terminology]: & Add Folder to Top → 增加文件夹到顶端( A)

### Ke4a42dc6389d:es (KDE4/es, band 85-94, fuzzy 86) ΔKiwi -0.158

- **Source:** Use this button to record this transaction
- **Zero-shot:** Use este botón para registrar esta transacción
- **draft_ctx:** Use este botón para registrar este asiento
- **Reference (not shown to any system or evaluator):** Use este botón para ingresar este asiento
- TM [partial]: Use this button to skip this transaction → Use este botón para saltear este asiento
- TM [partial]: Use this button to show the generated report information about this crash. → Use este botón para mostrar la información del reporte generada de este fallo. @info/ plain
- TM [terminology]: Click this button to accept the invitation. → Pulse este botón para aceptar la invitación. @action: button

## draft_ctx: Improvements

### Ef33912f6d25b:es (EMEA/es, band 75-84, fuzzy 80) ΔKiwi +0.316

- **Source:** BEFORE YOU ARE GIVEN Optimark
- **Zero-shot:** ANTES DE QUE SE LE ADMINISTRE Optimark
- **draft_ctx:** ANTES DE RECIBIR Optimark
- **Reference (not shown to any system or evaluator):** ANTES DE QUE SE LE ADMINISTRE Optimark
- TM [partial]: BEFORE YOU ARE GIVEN GEMZAR → ANTES DE USAR GEMZAR
- TM [partial]: BEFORE YOU ARE GIVEN SIMULECT → ANTES DE RECIBIR SIMULECT
- TM [partial]: BEFORE YOU ARE GIVEN YONDELIS → ANTES DE USAR YONDELIS

### Ka4ac2084f554:es (KDE4/es, band 85-94, fuzzy 90) ΔKiwi +0.167

- **Source:** The value the zoom-out tool should use.
- **Zero-shot:** El valor que debe usar la herramienta de alejar.
- **draft_ctx:** El valor que la herramienta de alejamiento debería usar
- **Reference (not shown to any system or evaluator):** El valor de alejamiento que la herramienta debería usar.
- TM [full]: The value the zoom-out tool should use → El valor que la herramienta de alejamiento debería usar
- TM [partial]: The value the zoom-in tool should use → El valor que la herramienta de aumento debería usar
- TM [none]: Select the zoom factor. → Seleccione el factor de ampliación.

### Ea238aebc5300:es (EMEA/es, band 75-84, fuzzy 82) ΔKiwi +0.072

- **Source:** The grounds for referral were submitted on 10 February 1997 and are appended to this opinion.
- **Zero-shot:** Los motivos del procedimiento de consulta se presentaron el 10 de febrero de 1997 y se adjuntan a la presente dictamen.
- **draft_ctx:** Los fundamentos de la remisión fueron enviados el 10 de febrero de 1997 y se adjuntan a este dictamen.
- **Reference (not shown to any system or evaluator):** El fundamento de la remisión se presentó ante la EMEA el 10 de febrero de 1997 y se adjunta a este dictamen.
- TM [full]: The grounds for referral were submitted on 12 October 1998 and are appended to this opinion. → Los fundamentos de la remisión fueron enviados el 12 de octubre de 1998 y se adjuntan a este dictamen.
- TM [terminology]: The marketing authorisation was renewed on 10 February 2002 and on 10 February 2007. → La autorización de comercialización fue renovada el 10 de febrero de 2002 y el 10 de febrero de 2007.
- TM [misleading]: The grounds for appeal were jointly lodged by the marketing authorisation holders on 11 August 1995. → Las razones alegadas para el recurso fueron presentadas conjuntamente por los titulares de la autorización de comercialización el día 11 de agosto de 1995.

### Ka634ad575582:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 75) ΔKiwi +0.067

- **Source:** Mail Conduit for KPilot
- **Zero-shot:** KPilot 的邮件传输代理
- **draft_ctx:** KPilot 的 Mail 管道
- **Reference (not shown to any system or evaluator):** KPilot 的 Mail 管道
- TM [partial]: Keyring Conduit for KPilot → KPilot 的密钥串管道
- TM [partial]: Configures the Mail Conduit for KPilot → 配置 KPilot 的 Mail 管道
- TM [partial]: Memofile Conduit for KPilot → KPilot 的备忘录管道

### K2da715fa5a9f:es (KDE4/es, band 75-84, fuzzy 75) ΔKiwi +0.057

- **Source:** Toggle display of Jupiter
- **Zero-shot:** Alternar visualización de Júpiter
- **draft_ctx:** Mostrar/ Ocultar Júpiter
- **Reference (not shown to any system or evaluator):** Mostrar/ Ocultar Júpiter
- TM [full]: Toggle display of Venus → Mostrar/ Ocultar Venus
- TM [full]: Toggle display of Mercury → Mostrar/ Ocultar Mercurio
- TM [full]: Toggle display of Pluto → Mostrar/ Ocultar Plutón

### E44d806f4707a:es (EMEA/es, band 50-74, fuzzy 50) ΔKiwi +0.054

- **Source:** FIRMAGON 80 mg powder for injection degarelix SC use only
- **Zero-shot:** FIRMAGON 80 mg polvo para solución para inyección degarelix solo para uso SC
- **draft_ctx:** FIRMAGON 80 mg polvo para solución inyectable degarelix solo para uso subcutáneo
- **Reference (not shown to any system or evaluator):** FIRMAGON 80 mg polvo para inyectable Degarelix Sólo para vía SC
- TM [partial]: PegIntron 80 micrograms powder for injection SC → PegIntron 80 microgramos polvo para solución inyectable Vía subcutánea
- TM [partial]: FIRMAGON 80 mg powder and solvent for solution for injection → FIRMAGON 80 mg polvo y disolvente para solución inyectable
- TM [partial]: Enbrel 25 mg powder for injection etanercept Subcutaneous use → Enbrel 25 mg polvo para inyección Etanercept Vía subcutánea.

## semantic_ctx: Degradations

### Ke4a42dc6389d:es (KDE4/es, band 85-94, fuzzy 86) ΔKiwi -0.261

- **Source:** Use this button to record this transaction
- **Zero-shot:** Use este botón para registrar esta transacción
- **semantic_ctx:** Use este botón para ingresar este asiento
- **Reference (not shown to any system or evaluator):** Use este botón para ingresar este asiento
- TM [partial]: Record this transaction into the register → Ingresar este asiento en el registro
- TM [partial]: Use this button to skip this transaction → Use este botón para saltear este asiento
- TM [terminology]: Use this to schedule the transaction for later entry into the ledger. → Utilice esto para planificar el asiento para ingresarlo posteriormente al libro mayor

### Ka43608cada29:es (KDE4/es, band 75-84, fuzzy 80) ΔKiwi -0.166

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** Geométrico - Flecha izquierda con muesca
- **semantic_ctx:** Geometría - Flecha izquierda irregular
- **Reference (not shown to any system or evaluator):** Geometría - Flecha izquierda irregularStencils
- TM [partial]: Geometric - Notched Right Arrow → Geometría - Flecha derecha irregularStencils
- TM [terminology]: Geometric - Left-Right Arrow → Geometría - Flecha izquierda-derechaStencils
- TM [terminology]: Geometric - Left-Right-Up Arrow → Geometría - Flecha izquierda-derecha-arribaStencils

### Kfb4f23faf64d:es (KDE4/es, band 50-74, fuzzy 50) ΔKiwi -0.164

- **Source:** Delete Sieve Script Confirmation
- **Zero-shot:** Confirmación de eliminación del script Sieve
- **semantic_ctx:** Confirmación para eliminar el guión de Sieve
- **Reference (not shown to any system or evaluator):** Conformación de borrado de guión de Sieve
- TM [terminology]: Confirm Quit From System Tray → Confirmar salir desde la bandeja del sistema
- TM [partial]: Undo File Copy Confirmation → Confirmación para deshacer la copia de archivo
- TM [terminology]: The Sieve script was successfully uploaded. → El guión de Sieve se publicó correctamente.

### K0819f3f5afd7:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 75) ΔKiwi -0.163

- **Source:** & Copy Folders To
- **Zero-shot:** &复制文件夹到
- **semantic_ctx:** 文件夹复制至( C)
- **Reference (not shown to any system or evaluator):** 文件夹复制至( C)
- TM [full]: & Copy Folder To → 文件夹复制至( C)
- TM [partial]: & Move Folder To → 文件夹移至( M)
- TM [terminology]: Copy Messages to Folder → 复制信件到文件夹

### E9c3c6005a3ff:es (EMEA/es, band 85-94, fuzzy 93) ΔKiwi -0.153

- **Source:** Route of Administration Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use
- **Zero-shot:** Vía de administración Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral Uso oral
- **semantic_ctx:** Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral
- **Reference (not shown to any system or evaluator):** Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral
- TM [partial]: Route of Administration Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use → Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral
- TM [partial]: Route of Administration Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use → Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral
- TM [partial]: Route of administration Oral use Oral use Oral use Oral use Oral use Oral use Oral use Oral use → Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral Vía oral

### Ka43608cada29:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 80) ΔKiwi -0.146

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** 几何 - 左向缺口箭头
- **semantic_ctx:** 几何 - 有锯齿的左箭头Stencils
- **Reference (not shown to any system or evaluator):** 几何 - 带锯齿的左箭头Stencils
- TM [partial]: Geometric - Notched Right Arrow → 几何 - 有锯齿的右箭头Stencils
- TM [terminology]: Geometric - Left-Right Arrow → 几何 - 左右箭头Stencils
- TM [terminology]: Geometric - Left-Right-Up Arrow → 几何 - 左右上箭头Stencils

## semantic_ctx: Improvements

### Ka43608cada29:de (KDE4/de, band 75-84, fuzzy 80) ΔKiwi +0.173

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** Geometrisch - Einkerbung Pfeil links
- **semantic_ctx:** Geometrie - Eingekerbter Pfeil nach links
- **Reference (not shown to any system or evaluator):** Geometrie - Eingekerbter Pfeil nach linksStencils
- TM [partial]: Geometric - Notched Right Arrow → Geometrie - Eingekerbter Pfeil nach rechtsStencils
- TM [terminology]: Geometric - Left-Right Arrow → Geometrie - Pfeil nach links und rechtsStencils
- TM [terminology]: Geometric - Left-Right-Up Arrow → Geometrie - Pfeil nach links, rechts und obenStencils

### Ka4ac2084f554:es (KDE4/es, band 85-94, fuzzy 90) ΔKiwi +0.167

- **Source:** The value the zoom-out tool should use.
- **Zero-shot:** El valor que debe usar la herramienta de alejar.
- **semantic_ctx:** El valor que la herramienta de alejamiento debería usar
- **Reference (not shown to any system or evaluator):** El valor de alejamiento que la herramienta debería usar.
- TM [full]: The value the zoom-out tool should use → El valor que la herramienta de alejamiento debería usar
- TM [partial]: The value the zoom-in tool should use → El valor que la herramienta de aumento debería usar
- TM [none]: Select the zoom factor. → Seleccione el factor de ampliación.

### Ea238aebc5300:es (EMEA/es, band 75-84, fuzzy 82) ΔKiwi +0.072

- **Source:** The grounds for referral were submitted on 10 February 1997 and are appended to this opinion.
- **Zero-shot:** Los motivos del procedimiento de consulta se presentaron el 10 de febrero de 1997 y se adjuntan a la presente dictamen.
- **semantic_ctx:** Los fundamentos de la remisión fueron enviados el 10 de febrero de 1997 y se adjuntan a este dictamen.
- **Reference (not shown to any system or evaluator):** El fundamento de la remisión se presentó ante la EMEA el 10 de febrero de 1997 y se adjunta a este dictamen.
- TM [full]: The grounds for referral were submitted on 12 October 1998 and are appended to this opinion. → Los fundamentos de la remisión fueron enviados el 12 de octubre de 1998 y se adjuntan a este dictamen.
- TM [none]: Membership of the Board in 1997 is given in Annex 1. → En el Anexo 1 se indica la composición del Consejo en 1997.
- TM [terminology]: The CPMP at its meetings of 17-19 November 1997 and of 23-25 February 1998 considered the issues raised by the referral and, based on all the information brought to its attention, reached the following conclusions: → En sus reuniones celebradas entre el 17 y el 19 de noviembre de 1997, y el 23-25 de febrero de 1998, el CPMP consideró la cuestión y llegó a las conclusiones siguientes:

### Ka634ad575582:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 75) ΔKiwi +0.067

- **Source:** Mail Conduit for KPilot
- **Zero-shot:** KPilot 的邮件传输代理
- **semantic_ctx:** KPilot 的 Mail 管道
- **Reference (not shown to any system or evaluator):** KPilot 的 Mail 管道
- TM [partial]: Configures the Mail Conduit for KPilot → 配置 KPilot 的 Mail 管道
- TM [partial]: Contacts Conduit for KPilot → KPilot 的联系人管道
- TM [partial]: Keyring Conduit for KPilot → KPilot 的密钥串管道

### K2da715fa5a9f:es (KDE4/es, band 75-84, fuzzy 75) ΔKiwi +0.057

- **Source:** Toggle display of Jupiter
- **Zero-shot:** Alternar visualización de Júpiter
- **semantic_ctx:** Mostrar/ Ocultar Júpiter
- **Reference (not shown to any system or evaluator):** Mostrar/ Ocultar Júpiter
- TM [full]: Toggle display of Pluto → Mostrar/ Ocultar Plutón
- TM [full]: Toggle display of Mercury → Mostrar/ Ocultar Mercurio
- TM [partial]: Toggle display of planet images → Mostrar/ Ocultar imágenes de planetas

### K513d085d6ce8:es (KDE4/es, band 50-74, fuzzy 57) ΔKiwi +0.055

- **Source:** No permission to cancel pending shutdown:
- **Zero-shot:** Sin permiso para cancelar el apagado pendiente:
- **semantic_ctx:** No hay permiso para cancelar el apagado pendiente:
- **Reference (not shown to any system or evaluator):** No hay permiso para cancelar el apagado pendiente: start of shutdown:
- TM [partial]: No permission to abort active sessions: → No hay permiso para terminar las sesiones activas: @title: column
- TM [terminology]: Will not lock the session, as unlocking would be impossible: → No bloqueará la sesión, ya que sería imposible desbloquearla:
- TM [none]: Unable to change job priority: → Imposible cambiar la prioridad del trabajo:

## fuzzy_ctx: Degradations

### Ka43608cada29:es (KDE4/es, band 75-84, fuzzy 80) ΔKiwi -0.166

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** Geométrico - Flecha izquierda con muesca
- **fuzzy_ctx:** Geometría - Flecha izquierda irregular
- **Reference (not shown to any system or evaluator):** Geometría - Flecha izquierda irregularStencils
- TM [partial]: Geometric - Notched Right Arrow → Geometría - Flecha derecha irregularStencils
- TM [terminology]: Geometric - Up Arrow → Geometría - Flecha arribaStencils
- TM [terminology]: Geometric - Up-Down-Left Arrow → Geometría - Flecha arriba-abajo-izquierdaStencils

### Kfb4f23faf64d:es (KDE4/es, band 50-74, fuzzy 50) ΔKiwi -0.164

- **Source:** Delete Sieve Script Confirmation
- **Zero-shot:** Confirmación de eliminación del script Sieve
- **fuzzy_ctx:** Confirmación de eliminación del guión de Sieve
- **Reference (not shown to any system or evaluator):** Conformación de borrado de guión de Sieve
- TM [misleading]: Delete permanently without confirmation → Eliminar permanentemente sin confirmación
- TM [terminology]: Delete user from group script: → Guión para eliminar usuario de grupo:
- TM [terminology]: The Sieve script was successfully uploaded. → El guión de Sieve se publicó correctamente.

### K0819f3f5afd7:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 75) ΔKiwi -0.163

- **Source:** & Copy Folders To
- **Zero-shot:** &复制文件夹到
- **fuzzy_ctx:** 文件夹复制至( C)
- **Reference (not shown to any system or evaluator):** 文件夹复制至( C)
- TM [full]: & Copy Folder To → 文件夹复制至( C)
- TM [terminology]: & Copy Link Address → 复制链接地址( C)
- TM [terminology]: & Copy Global Templates → 复制全局模板( C)

### Ke4a42dc6389d:es (KDE4/es, band 85-94, fuzzy 86) ΔKiwi -0.158

- **Source:** Use this button to record this transaction
- **Zero-shot:** Use este botón para registrar esta transacción
- **fuzzy_ctx:** Use este botón para registrar este asiento
- **Reference (not shown to any system or evaluator):** Use este botón para ingresar este asiento
- TM [partial]: Use this button to skip this transaction → Use este botón para saltear este asiento
- TM [partial]: Use this button to close the window → Use este botón para cerrar la ventana
- TM [style_convention]: Use this button to update all image fingerprints. → Active esta opción para actualizar las impresiones digitales de las imagenes.

### Ka43608cada29:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 80) ΔKiwi -0.146

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** 几何 - 左向缺口箭头
- **fuzzy_ctx:** 几何 - 有锯齿的左箭头Stencils
- **Reference (not shown to any system or evaluator):** 几何 - 带锯齿的左箭头Stencils
- TM [partial]: Geometric - Notched Right Arrow → 几何 - 有锯齿的右箭头Stencils
- TM [terminology]: Geometric - Up Arrow → 几何 - 上箭头Stencils
- TM [terminology]: Geometric - Up-Down-Left Arrow → 几何 - 上下左箭头Stencils

### Ke89f6b6a5911:es (KDE4/es, band 50-74, fuzzy 50) ΔKiwi -0.134

- **Source:** Restore Layouts to Default
- **Zero-shot:** Restaurar diseños predeterminados
- **fuzzy_ctx:** Restaurar las disposiciones a predeterminado
- **Reference (not shown to any system or evaluator):** Volver a la disposición predeterminada
- TM [partial]: & Restore to Default → & Restaurar a predeterminado
- TM [terminology]: Save Layouts as Default → Guardar la disposición como predeterminada
- TM [none]: & Go to Default Key → & Ir a la clave predeterminada

## fuzzy_ctx: Improvements

### Ka4ac2084f554:es (KDE4/es, band 85-94, fuzzy 90) ΔKiwi +0.174

- **Source:** The value the zoom-out tool should use.
- **Zero-shot:** El valor que debe usar la herramienta de alejar.
- **fuzzy_ctx:** El valor que la herramienta de alejamiento debería usar.
- **Reference (not shown to any system or evaluator):** El valor de alejamiento que la herramienta debería usar.
- TM [full]: The value the zoom-out tool should use → El valor que la herramienta de alejamiento debería usar
- TM [partial]: The value the zoom-in tool should use → El valor que la herramienta de aumento debería usar
- TM [partial]: The identifier the daemon should use. → El identificador que debería usar el demonio.

### Ka43608cada29:de (KDE4/de, band 75-84, fuzzy 80) ΔKiwi +0.173

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** Geometrisch - Einkerbung Pfeil links
- **fuzzy_ctx:** Geometrie - Eingekerbter Pfeil nach links
- **Reference (not shown to any system or evaluator):** Geometrie - Eingekerbter Pfeil nach linksStencils
- TM [partial]: Geometric - Notched Right Arrow → Geometrie - Eingekerbter Pfeil nach rechtsStencils
- TM [partial]: Geometric - Up Arrow → Geometrie - Pfeil nach obenStencils
- TM [terminology]: Geometric - Up-Down-Left Arrow → Geometrie - Pfeil nach oben, unten und linksStencils

### E44d806f4707a:es (EMEA/es, band 50-74, fuzzy 50) ΔKiwi +0.089

- **Source:** FIRMAGON 80 mg powder for injection degarelix SC use only
- **Zero-shot:** FIRMAGON 80 mg polvo para solución para inyección degarelix solo para uso SC
- **fuzzy_ctx:** FIRMAGON 80 mg polvo para inyección degarelix Solo para uso subcutáneo
- **Reference (not shown to any system or evaluator):** FIRMAGON 80 mg polvo para inyectable Degarelix Sólo para vía SC
- TM [partial]: Enbrel 25 mg powder for injection etanercept Subcutaneous use → Enbrel 25 mg polvo para inyección Etanercept Vía subcutánea.
- TM [partial]: Enbrel 50 mg powder for injection etanercept Subcutaneous use → Enbrel 50 mg polvo para inyección etanercept Vía subcutánea.
- TM [partial]: PegIntron 80 micrograms powder for injection SC → PegIntron 80 microgramos polvo para solución inyectable Vía subcutánea

### Ka634ad575582:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 75) ΔKiwi +0.073

- **Source:** Mail Conduit for KPilot
- **Zero-shot:** KPilot 的邮件传输代理
- **fuzzy_ctx:** KPilot 的邮件管道
- **Reference (not shown to any system or evaluator):** KPilot 的 Mail 管道
- TM [partial]: Keyring Conduit for KPilot → KPilot 的密钥串管道
- TM [partial]: Memofile Conduit for KPilot → KPilot 的备忘录管道
- TM [partial]: Calendar Conduit for KPilot → KPilot 的日历管道

### Ea238aebc5300:es (EMEA/es, band 75-84, fuzzy 82) ΔKiwi +0.072

- **Source:** The grounds for referral were submitted on 10 February 1997 and are appended to this opinion.
- **Zero-shot:** Los motivos del procedimiento de consulta se presentaron el 10 de febrero de 1997 y se adjuntan a la presente dictamen.
- **fuzzy_ctx:** Los fundamentos de la remisión fueron enviados el 10 de febrero de 1997 y se adjuntan a este dictamen.
- **Reference (not shown to any system or evaluator):** El fundamento de la remisión se presentó ante la EMEA el 10 de febrero de 1997 y se adjunta a este dictamen.
- TM [full]: The grounds for referral were submitted on 12 October 1998 and are appended to this opinion. → Los fundamentos de la remisión fueron enviados el 12 de octubre de 1998 y se adjuntan a este dictamen.
- TM [terminology]: The marketing authorisation was renewed on 10 February 2002 and on 10 February 2007. → La autorización de comercialización fue renovada el 10 de febrero de 2002 y el 10 de febrero de 2007.
- TM [misleading]: The grounds for the referral were concerns over the insufficiency of the clinical data submitted to establish the efficacy of the product. → Los motivos para el arbitraje fueron las dudas respecto a la insuficiencia de los datos clínicos presentados para determinar la eficacia del producto.

### K2da715fa5a9f:es (KDE4/es, band 75-84, fuzzy 75) ΔKiwi +0.057

- **Source:** Toggle display of Jupiter
- **Zero-shot:** Alternar visualización de Júpiter
- **fuzzy_ctx:** Mostrar/ Ocultar Júpiter
- **Reference (not shown to any system or evaluator):** Mostrar/ Ocultar Júpiter
- TM [full]: Toggle display of Venus → Mostrar/ Ocultar Venus
- TM [partial]: Toggle display of Stars → Mostrar/ Ocultar estrellas
- TM [full]: Toggle display of Mercury → Mostrar/ Ocultar Mercurio
