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

### Ke4a42dc6389d:es (KDE4/es, band 85-94, fuzzy 86) ΔKiwi -0.158

- **Source:** Use this button to record this transaction
- **Zero-shot:** Use este botón para registrar esta transacción
- **hybrid_ctx:** Use este botón para registrar este asiento
- **Reference (not shown to any system or evaluator):** Use este botón para ingresar este asiento
- TM [partial]: Use this button to skip this transaction → Use este botón para saltear este asiento
- TM [partial]: Use this button to show the generated report information about this crash. → Use este botón para mostrar la información del reporte generada de este fallo. @info/ plain
- TM [terminology]: Click this button to accept the invitation. → Pulse este botón para aceptar la invitación. @action: button

### Ka43608cada29:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 80) ΔKiwi -0.146

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** 几何 - 左向缺口箭头
- **hybrid_ctx:** 几何 - 有锯齿的左箭头Stencils
- **Reference (not shown to any system or evaluator):** 几何 - 带锯齿的左箭头Stencils
- TM [partial]: Geometric - Notched Right Arrow → 几何 - 有锯齿的右箭头Stencils
- TM [terminology]: Geometric - Left-Right Arrow → 几何 - 左右箭头Stencils
- TM [terminology]: Geometric - Up Arrow → 几何 - 上箭头Stencils

### K692786e06f39:es (KDE4/es, band 85-94, fuzzy 90) ΔKiwi -0.060

- **Source:** The requested device could not be initialized ("mounted"). The reported error was: %1
- **Zero-shot:** No se pudo inicializar ("montar") el dispositivo solicitado. El error reportado fue: %1
- **hybrid_ctx:** El dispositivo solicitado no se pudo desinicializar («montar»). El error emitido fue: %1
- **Reference (not shown to any system or evaluator):** El dispositivo solicitado no se pudo inicializar (« montar »). El error emitido fue: %1
- TM [partial]: The requested device could not be uninitialized ("unmounted"). The reported error was: %1 → El dispositivo solicitado no se pudo desinicializar (« desmontar »). El error emitido fue: %1
- TM [misleading]: Could not unmount device. The reported error was: %1 → No se pudo desmontar el dispositivo. El mensaje de error fue: %1
- TM [partial]: Could not mount device. The reported error was: %1 → No se pudo montar el dispositivo. El mensaje de error fue: %1

### K7ede7068b57a:es (KDE4/es, band 95-99, fuzzy 96) ΔKiwi -0.038

- **Source:** You did not select an encryption key for one of the recipients; this person will not be able to decrypt the message if you encrypt it.
- **Zero-shot:** No ha seleccionado una clave de cifrado para uno de los destinatarios; esta persona no podrá descifrar el mensaje si lo cifra.
- **hybrid_ctx:** No seleccionó una clave de cifrado para uno de los destinatarios; esta persona no podrá descifrar el mensaje si lo cifra.
- **Reference (not shown to any system or evaluator):** No ha seleccionado una clave de cifrado para uno de los destinatarios. Si cifra el mensaje, esa persona no podrá descifrarlo.
- TM [full]: You did not select an encryption key for one of the recipients: this person will not be able to decrypt the message if you encrypt it. → No seleccionó una clave de cifrado para alguno de los destinatarios. Esta persona no podrá descifrar el mensaje si lo cifra.
- TM [partial]: You did not select encryption keys for some of the recipients; these persons will not be able to decrypt the message if you encrypt it. → No ha seleccionado clave de cifrado para algunos de los destinatarios del mensaje. Si cifra el mensaje, esas personas no podrán descifrarlo.
- TM [partial]: You did not select an encryption key for any of the recipients of this message; therefore, the message will not be encrypted. → No seleccionó una clave de cifrado para alguno de los destinatarios de este mensaje. Por lo tanto, el mensaje no se cifrará.

### Kfef00712051a:es (KDE4/es, band 50-74, fuzzy 50) ΔKiwi -0.035

- **Source:** Pan the image to a region
- **Zero-shot:** Desplace la imagen hacia una región
- **hybrid_ctx:** Posicionar la imagen en una región
- **Reference (not shown to any system or evaluator):** Desplazar la imagen hacia una región
- TM [misleading]: Panning with the mouse → Posicionarse con el ratón
- TM [terminology]: Save image to a file → Guardar imagen en un archivo
- TM [none]: Save the selection to a file → Guardar la selección en un archivo

## hybrid_ctx: Improvements

### Ka43608cada29:de (KDE4/de, band 75-84, fuzzy 80) ΔKiwi +0.173

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** Geometrisch - Einkerbung Pfeil links
- **hybrid_ctx:** Geometrie - Eingekerbter Pfeil nach links
- **Reference (not shown to any system or evaluator):** Geometrie - Eingekerbter Pfeil nach linksStencils
- TM [partial]: Geometric - Notched Right Arrow → Geometrie - Eingekerbter Pfeil nach rechtsStencils
- TM [terminology]: Geometric - Left-Right Arrow → Geometrie - Pfeil nach links und rechtsStencils
- TM [partial]: Geometric - Up Arrow → Geometrie - Pfeil nach obenStencils

### E8925bc1668d3:es (EMEA/es, band 50-74, fuzzy 71) ΔKiwi +0.043

- **Source:** Patients receiving VIRACEPT TID (n=11) achieved nelfinavir peak plasma concentrations (Cmax) of 3.0 ± 1.6 µg/ml and morning and evening trough concentrations of 1.4 ± 0.6 µg/ml and 1.0 ± 0.5 µg/ml, respectively.
- **Zero-shot:** Los pacientes que recibieron VIRACEPT tres veces al día (n=11) alcanzaron concentraciones plasmáticas máximas (Cmax) de nelfinavir de 3,0 ± 1,6 µg/ml y concentraciones valle matutinas y vespertinas de 1,4 ± 0,6 µg/ml y 1,0 ± 0,5 µg/ml, respectivamente.
- **hybrid_ctx:** Los pacientes que recibían VIRACEPT TID (n=11) alcanzaron concentraciones plasmáticas máximas (Cmax) de nelfinavir de 3,0 ± 1,6 µg/ml y concentraciones mínimas por la mañana y por la noche de 1,4 ± 0,6 µg/ml y 1,0 ± 0,5 µg/ml, respectivamente.
- **Reference (not shown to any system or evaluator):** Los pacientes que recibieron VIRACEPT TID (n=11) alcanzaron concentraciones máximas en plasma (Cmax) de 3,0 ± 1,6 µg/ml y concentraciones mínimas por la mañana y por la noche de 1,4 ± 0,6 µg/ml y 1,0 ± 0,5 µg/ml, respectivamente.
- TM [partial]: Patients receiving VIRACEPT BID (n=10) achieved nelfinavir Cmax of 4.0 ± 0.8 µg/ml and morning and evening trough concentrations of 2.2 ± 1.3 µg/ml and 0.7 ± 0.4 µg/ml, respectively. → Los pacientes que recibían VIRACEPT BID (n = 10) alcanzaron una Cmax de nelfinavir de 4,0±0,8 µg/ml y concentraciones mínimas por la mañana y por la noche de 2,2±1,3 µg/ml y 0,7±0,4 µg/ml, respectivamente.
- TM [none]: maximum plasma concentrations (Tmax) between 1– 1.5 hours and 1.5– 3.7 hours after administration, respectively. → Loratadina y DL alcanzan las concentraciones plasmáticas máximas (Tmax) entre 1– 1,5 horas y 1,5– 3,7 horas después de su administración, respectivamente.
- TM [style_convention]: Peak concentrations (Cmax) are typically 31 and 43 µg/ ml following a single 1,000 mg dose and repeated 1,000 mg twice daily dose, respectively. → Los valores normales del pico plasmático (Cmax) después de una dosis simple de 1.000 mg y de una dosis repetida de 1.000 mg dos veces al día son del 31 y 43 μ g/ ml respectivamente.

### K692786e06f39:zh_CN (KDE4/zh_CN, band 85-94, fuzzy 90) ΔKiwi +0.036

- **Source:** The requested device could not be initialized ("mounted"). The reported error was: %1
- **Zero-shot:** 无法初始化（“挂载”）请求的设备。报告的错误为：%1
- **hybrid_ctx:** 请求的设备无法被初始化（“挂载”）。报告的错误为：%1
- **Reference (not shown to any system or evaluator):** 请求的设备无法被初始化 (“ 被挂载 ”) 。 报告的错误是 ：% 1
- TM [misleading]: The requested device could not be uninitialized ("unmounted"). The reported error was: %1 → 请求的设备无法被卸载。 报告的错误是 ：% 1
- TM [misleading]: Could not unmount device. The reported error was: %1 → 无法卸载设备 。 报告的错误为 ：% 1
- TM [partial]: Could not mount device. The reported error was: %1 → 无法挂载设备 。 报告的错误为 ：% 1

### K550a1f803a1b:zh_CN (KDE4/zh_CN, band <50, fuzzy 43) ΔKiwi +0.014

- **Source:** Mails on the server in folder %1 were deleted. Do you want to delete them locally? UIDs: %2
- **Zero-shot:** 文件夹 %1 中服务器上的邮件已被删除。是否要在本地删除它们？UID： %2
- **hybrid_ctx:** 服务器文件夹 %1 中的邮件已被删除。您想要在本地删除它们吗？UID： %2
- **Reference (not shown to any system or evaluator):** 文件夹% 1 内的信件已经在服务器上被删除。 您想要在本地删除它们吗 ？ UID ：% 2
- TM [misleading]: It seems that the folder %1 was deleted. Do you want to delete it from the server? → 似乎文件夹% 1 已删除。 您想要从服务器上删除吗 ？
- TM [style_convention]: The folder %1 does not exist. Do you want to create it now? → 文件夹% 1 不存在。 您要现在创建吗 ？
- TM [terminology]: Error while deleting folder %1 on the server: → 在服务器上删除文件夹% 1 出错 ：

### Kaa5339f3ff22:zh_CN (KDE4/zh_CN, band 100, fuzzy 100) ΔKiwi +0.012

- **Source:** Find text Shows a dialog that allows you to find text on the displayed page.
- **Zero-shot:** 查找文本 显示一个允许您在当前显示页面中查找文本的对话框。
- **hybrid_ctx:** 查找文本 显示一个对话框，让您可以在所显示的页面中查找文本。
- **Reference (not shown to any system or evaluator):** 查找文本 将显示一个让您在所显示页面中查找文本的对话框 。 @ title: menu HTML frame/ iframe
- TM [full]: Find text Shows a dialog that allows you to find text on the displayed page. → 查找文本 显示一个对话框， 让您可以在所显示的页面中查找文本 。
- TM [partial]: Configure Notifications Shows a dialog that lets you configure notifications. → 配置通知 显示一个让您配置通知的对话框 。
- TM [terminology]: Shows a list of strings to search for (and if you specified it, a list of strings to replace with). Use the "add strings" dialog to edit your string list or double click on a string. → 显示搜索字符串列表( 如果您明确要求， 则由指定字符串替换显示) 。 使用“ 添加字符串” 对话框可编辑您的字符串列表， 或者双击字符串也可执行操作 。

### K7ede7068b57a:zh_CN (KDE4/zh_CN, band 95-99, fuzzy 96) ΔKiwi +0.006

- **Source:** You did not select an encryption key for one of the recipients; this person will not be able to decrypt the message if you encrypt it.
- **Zero-shot:** 您未为其中一名收件人选择加密密钥；如果您对其进行加密，该人员将无法解密此消息。
- **hybrid_ctx:** 您没有为其中一名收件人选择加密密钥；如果您加密此信件，该收件人将无法解密。
- **Reference (not shown to any system or evaluator):** 您没有选择给该信件收件人其中之一的加密密钥， 如果您加密此信件， 此收件人无法将其解密 。
- TM [full]: You did not select an encryption key for one of the recipients: this person will not be able to decrypt the message if you encrypt it. → 您没有为此信件的收件人之一选择加密密钥； 因此， 如果您加密的话， 该收件人将无法解密此信件 。
- TM [partial]: You did not select encryption keys for some of the recipients; these persons will not be able to decrypt the message if you encrypt it. → 您没有选择给一部分收件人的加密密钥， 如果您加密此信件， 这些人无法将其解密 。
- TM [partial]: You did not select an encryption key for any of the recipients of this message; therefore, the message will not be encrypted. → 您没有为此信件的任何一个收件人选择加密密钥； 因此， 无法加密此信件 。

## structured_ctx: Degradations

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

### Ke4a42dc6389d:de (KDE4/de, band 85-94, fuzzy 86) ΔKiwi -0.075

- **Source:** Use this button to record this transaction
- **Zero-shot:** Verwenden Sie diese Schaltfläche, um diese Transaktion aufzuzeichnen
- **structured_ctx:** Drücken, um diese Buchung aufzunehmen
- **Reference (not shown to any system or evaluator):** Drücken, um die Buchung aufzunehmen
- TM [partial]: Use this button to skip this transaction → Drücken, um die Buchung zu überspringen
- TM [style_convention]: Use this button to show the generated report information about this crash. → Klicken Sie auf diesen Knopf, um den erzeugten Fehlerbericht zu diesem Absturz einzusehen.@info/plain
- TM [style_convention]: Click this button to accept the invitation. → Drücken Sie diesen Knopf, um die Einladung anzunehmen.@action:button

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "transaction" → "Buchung"
- "button" → "Knopf"

Phrasing in previous translations:
- "Use this button to" → "Drücken, um"

Differences from the historical segments (do not carry these over):
- historical segment says 'skip'; new segment says 'record'
```

### K79c36708f4d3:zh_CN (KDE4/zh_CN, band <50, fuzzy 46) ΔKiwi -0.046

- **Source:** The pre shared key could not be found, check PSK settings.
- **Zero-shot:** 找不到预共享密钥，请检查 PSK 设置。
- **structured_ctx:** 找不到 Pre shared key，请检查 PSK 设置。
- **Reference (not shown to any system or evaluator):** 连接后 ping IP
- TM [style_convention]: Your secret key could not be exported. Check the key. → 您的绝密密钥无法导出 。 请检查该密钥是否有问题 。
- TM [style_convention]: The executable %1 could not be found in your PATH. → 在您的 PATH 中找不到可执行程序% 1 。
- TM [terminology]: Pre-shared key for authentication (shared secret) → Pre shared key

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "Pre-shared key" → "Pre shared key"

Phrasing in previous translations:
- "could not be found" → "找不到"

Differences from the historical segments (do not carry these over):
- Historical segment refers to 'secret key' (绝密密钥) and 'exported' (导出); new segment refers to 'pre shared key' and 'found'.
```

### K0de9eec90b8a:zh_CN (KDE4/zh_CN, band 95-99, fuzzy 96) ΔKiwi -0.033

- **Source:** The share "%1" could not be mounted. Detailed information cannot be provided because there was no error message.
- **Zero-shot:** 无法挂载共享文件夹“%1”。由于没有错误消息，无法提供详细信息。
- **structured_ctx:** 无法挂载该共享 "%1"。由于没有错误消息，无法提供详细信息。
- **Reference (not shown to any system or evaluator):** 无法卸载该共享！ 挂载点为空 。
- TM [misleading]: The share "%1" could not be unmounted. Detailed information cannot be provided because there was no error message. → 无法卸载该共享！ 挂载点为空 。
- TM [none]: The list of shares could not be retrieved. Detailed information cannot be provided because there was no error message. → 不能确定磁盘使用状态 。
- TM [none]: The preview could not be compiled. Detailed information cannot be provided because there was no error message. → 无法卸载该共享！ 挂载点为空 。

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "The share" → "该共享"

Phrasing in previous translations:
- "Detailed information cannot be provided because there was no error message." → "挂载点为空 。"

Differences from the historical segments (do not carry these over):
- historical segment says 'unmounted'; new segment says 'mounted'
```

### K7ede7068b57a:es (KDE4/es, band 95-99, fuzzy 96) ΔKiwi -0.033

- **Source:** You did not select an encryption key for one of the recipients; this person will not be able to decrypt the message if you encrypt it.
- **Zero-shot:** No ha seleccionado una clave de cifrado para uno de los destinatarios; esta persona no podrá descifrar el mensaje si lo cifra.
- **structured_ctx:** No seleccionó una clave de cifrado para alguno de los destinatarios; esta persona no podrá descifrar el mensaje si lo cifra.
- **Reference (not shown to any system or evaluator):** No ha seleccionado una clave de cifrado para uno de los destinatarios. Si cifra el mensaje, esa persona no podrá descifrarlo.
- TM [full]: You did not select an encryption key for one of the recipients: this person will not be able to decrypt the message if you encrypt it. → No seleccionó una clave de cifrado para alguno de los destinatarios. Esta persona no podrá descifrar el mensaje si lo cifra.
- TM [partial]: You did not select encryption keys for some of the recipients; these persons will not be able to decrypt the message if you encrypt it. → No ha seleccionado clave de cifrado para algunos de los destinatarios del mensaje. Si cifra el mensaje, esas personas no podrán descifrarlo.
- TM [partial]: You did not select an encryption key for any of the recipients of this message; therefore, the message will not be encrypted. → No seleccionó una clave de cifrado para alguno de los destinatarios de este mensaje. Por lo tanto, el mensaje no se cifrará.

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "encryption key" → "clave de cifrado"
- "recipients" → "destinatarios"
- "decrypt" → "descifrar"
- "message" → "mensaje"
- "encrypt" → "cifra"

Phrasing in previous translations:
- "You did not select an encryption key for one of the recipients" → "No seleccionó una clave de cifrado para alguno de los destinatarios"
- "this person will not be able to decrypt the message if you encrypt it" → "Esta persona no podrá descifrar el mensaje si lo cifra"

Spanish conventions seen in previous translations:
- Use formal address (usted) as evidenced by 'seleccionó' and 'cifra'.
```

## structured_ctx: Improvements

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

### E8925bc1668d3:es (EMEA/es, band 50-74, fuzzy 71) ΔKiwi +0.043

- **Source:** Patients receiving VIRACEPT TID (n=11) achieved nelfinavir peak plasma concentrations (Cmax) of 3.0 ± 1.6 µg/ml and morning and evening trough concentrations of 1.4 ± 0.6 µg/ml and 1.0 ± 0.5 µg/ml, respectively.
- **Zero-shot:** Los pacientes que recibieron VIRACEPT tres veces al día (n=11) alcanzaron concentraciones plasmáticas máximas (Cmax) de nelfinavir de 3,0 ± 1,6 µg/ml y concentraciones valle matutinas y vespertinas de 1,4 ± 0,6 µg/ml y 1,0 ± 0,5 µg/ml, respectivamente.
- **structured_ctx:** Los pacientes que recibían VIRACEPT TID (n=11) alcanzaron concentraciones plasmáticas máximas (Cmax) de nelfinavir de 3,0 ± 1,6 µg/ml y concentraciones mínimas por la mañana y por la noche de 1,4 ± 0,6 µg/ml y 1,0 ± 0,5 µg/ml, respectivamente.
- **Reference (not shown to any system or evaluator):** Los pacientes que recibieron VIRACEPT TID (n=11) alcanzaron concentraciones máximas en plasma (Cmax) de 3,0 ± 1,6 µg/ml y concentraciones mínimas por la mañana y por la noche de 1,4 ± 0,6 µg/ml y 1,0 ± 0,5 µg/ml, respectivamente.
- TM [partial]: Patients receiving VIRACEPT BID (n=10) achieved nelfinavir Cmax of 4.0 ± 0.8 µg/ml and morning and evening trough concentrations of 2.2 ± 1.3 µg/ml and 0.7 ± 0.4 µg/ml, respectively. → Los pacientes que recibían VIRACEPT BID (n = 10) alcanzaron una Cmax de nelfinavir de 4,0±0,8 µg/ml y concentraciones mínimas por la mañana y por la noche de 2,2±1,3 µg/ml y 0,7±0,4 µg/ml, respectivamente.
- TM [none]: maximum plasma concentrations (Tmax) between 1– 1.5 hours and 1.5– 3.7 hours after administration, respectively. → Loratadina y DL alcanzan las concentraciones plasmáticas máximas (Tmax) entre 1– 1,5 horas y 1,5– 3,7 horas después de su administración, respectivamente.
- TM [style_convention]: Peak concentrations (Cmax) are typically 31 and 43 µg/ ml following a single 1,000 mg dose and repeated 1,000 mg twice daily dose, respectively. → Los valores normales del pico plasmático (Cmax) después de una dosis simple de 1.000 mg y de una dosis repetida de 1.000 mg dos veces al día son del 31 y 43 μ g/ ml respectivamente.

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "nelfinavir" → "nelfinavir"
- "trough concentrations" → "concentraciones mínimas"
- "morning and evening" → "por la mañana y por la noche"

Phrasing in previous translations:
- "Patients receiving" → "Los pacientes que recibían"
- "respectively" → "respectivamente"

Spanish conventions seen in previous translations:
- Use comma as decimal separator (e.g., 4,0 instead of 4.0).

Differences from the historical segments (do not carry these over):
- historical segment says BID (n=10); new segment says TID (n=11)
- historical segment values are 4.0 ± 0.8, 2.2 ± 1.3, 0.7 ± 0.4; new segment values are 3.0 ± 1.6, 1.4 ± 0.6, 1.0 ± 0.5
```

### K692786e06f39:zh_CN (KDE4/zh_CN, band 85-94, fuzzy 90) ΔKiwi +0.038

- **Source:** The requested device could not be initialized ("mounted"). The reported error was: %1
- **Zero-shot:** 无法初始化（“挂载”）请求的设备。报告的错误为：%1
- **structured_ctx:** 请求的设备无法初始化（“挂载”）。报告的错误是：%1
- **Reference (not shown to any system or evaluator):** 请求的设备无法被初始化 (“ 被挂载 ”) 。 报告的错误是 ：% 1
- TM [misleading]: The requested device could not be uninitialized ("unmounted"). The reported error was: %1 → 请求的设备无法被卸载。 报告的错误是 ：% 1
- TM [misleading]: Could not unmount device. The reported error was: %1 → 无法卸载设备 。 报告的错误为 ：% 1
- TM [partial]: Could not mount device. The reported error was: %1 → 无法挂载设备 。 报告的错误为 ：% 1

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "The requested device" → "请求的设备"
- "mount" → "挂载"

Phrasing in previous translations:
- "The reported error was: %1" → "报告的错误是 ：% 1"

Simplified Chinese conventions seen in previous translations:
- Maintain the placeholder %1 in the target translation.

Differences from the historical segments (do not carry these over):
- Historical segment refers to 'uninitialized' ('unmounted'), whereas the new segment refers to 'initialized' ('mounted').
```

### K550a1f803a1b:zh_CN (KDE4/zh_CN, band <50, fuzzy 43) ΔKiwi +0.016

- **Source:** Mails on the server in folder %1 were deleted. Do you want to delete them locally? UIDs: %2
- **Zero-shot:** 文件夹 %1 中服务器上的邮件已被删除。是否要在本地删除它们？UID： %2
- **structured_ctx:** 服务器中文件夹% 1内的邮件已被删除。您是否想要在本地删除它们？UID：% 2
- **Reference (not shown to any system or evaluator):** 文件夹% 1 内的信件已经在服务器上被删除。 您想要在本地删除它们吗 ？ UID ：% 2
- TM [misleading]: It seems that the folder %1 was deleted. Do you want to delete it from the server? → 似乎文件夹% 1 已删除。 您想要从服务器上删除吗 ？
- TM [style_convention]: The folder %1 does not exist. Do you want to create it now? → 文件夹% 1 不存在。 您要现在创建吗 ？
- TM [terminology]: Error while deleting folder %1 on the server: → 在服务器上删除文件夹% 1 出错 ：

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "the folder %1" → "文件夹% 1"
- "the server" → "服务器"

Simplified Chinese conventions seen in previous translations:
- Placeholders like %1 are preserved with a space before the digit in the target translation (e.g., % 1).

Differences from the historical segments (do not carry these over):
- Historical segment refers to deleting the folder itself; new segment refers to deleting mails within the folder.
- Historical segment asks to delete from the server; new segment asks to delete locally.
```

### Kaa5339f3ff22:zh_CN (KDE4/zh_CN, band 100, fuzzy 100) ΔKiwi +0.012

- **Source:** Find text Shows a dialog that allows you to find text on the displayed page.
- **Zero-shot:** 查找文本 显示一个允许您在当前显示页面中查找文本的对话框。
- **structured_ctx:** 查找文本 显示一个对话框，让您可以在所显示的页面中查找文本。
- **Reference (not shown to any system or evaluator):** 查找文本 将显示一个让您在所显示页面中查找文本的对话框 。 @ title: menu HTML frame/ iframe
- TM [full]: Find text Shows a dialog that allows you to find text on the displayed page. → 查找文本 显示一个对话框， 让您可以在所显示的页面中查找文本 。
- TM [partial]: Configure Notifications Shows a dialog that lets you configure notifications. → 配置通知 显示一个让您配置通知的对话框 。
- TM [terminology]: Shows a list of strings to search for (and if you specified it, a list of strings to replace with). Use the "add strings" dialog to edit your string list or double click on a string. → 显示搜索字符串列表( 如果您明确要求， 则由指定字符串替换显示) 。 使用“ 添加字符串” 对话框可编辑您的字符串列表， 或者双击字符串也可执行操作 。

```
Reusable context extracted from previously approved translations in a translation memory. The historical segments were NOT translations of the source segment. Apply an item only where it fits the source segment, and always follow the meaning of the source segment.

Terminology in previous translations:
- "Find text" → "查找文本"
- "dialog" → "对话框"
- "displayed page" → "所显示的页面"

Phrasing in previous translations:
- "Shows a dialog that allows you to" → "显示一个对话框， 让您可以"
- "find text on the displayed page" → "在所显示的页面中查找文本"
```

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

### Ka43608cada29:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 80) ΔKiwi -0.146

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** 几何 - 左向缺口箭头
- **semantic_ctx:** 几何 - 有锯齿的左箭头Stencils
- **Reference (not shown to any system or evaluator):** 几何 - 带锯齿的左箭头Stencils
- TM [partial]: Geometric - Notched Right Arrow → 几何 - 有锯齿的右箭头Stencils
- TM [terminology]: Geometric - Left-Right Arrow → 几何 - 左右箭头Stencils
- TM [terminology]: Geometric - Left-Right-Up Arrow → 几何 - 左右上箭头Stencils

### Ke4a42dc6389d:de (KDE4/de, band 85-94, fuzzy 86) ΔKiwi -0.075

- **Source:** Use this button to record this transaction
- **Zero-shot:** Verwenden Sie diese Schaltfläche, um diese Transaktion aufzuzeichnen
- **semantic_ctx:** Drücken, um diese Buchung aufzunehmen
- **Reference (not shown to any system or evaluator):** Drücken, um die Buchung aufzunehmen
- TM [partial]: Record this transaction into the register → Buchung in das Kontobuch aufnehmen
- TM [partial]: Use this button to skip this transaction → Drücken, um die Buchung zu überspringen
- TM [terminology]: Use this to schedule the transaction for later entry into the ledger. → Drücken, um die Buchung für einen späteren Eintrag in das Kontobuch vorzusehen.

### K7ede7068b57a:es (KDE4/es, band 95-99, fuzzy 96) ΔKiwi -0.038

- **Source:** You did not select an encryption key for one of the recipients; this person will not be able to decrypt the message if you encrypt it.
- **Zero-shot:** No ha seleccionado una clave de cifrado para uno de los destinatarios; esta persona no podrá descifrar el mensaje si lo cifra.
- **semantic_ctx:** No seleccionó una clave de cifrado para uno de los destinatarios; esta persona no podrá descifrar el mensaje si lo cifra.
- **Reference (not shown to any system or evaluator):** No ha seleccionado una clave de cifrado para uno de los destinatarios. Si cifra el mensaje, esa persona no podrá descifrarlo.
- TM [full]: You did not select an encryption key for one of the recipients: this person will not be able to decrypt the message if you encrypt it. → No seleccionó una clave de cifrado para alguno de los destinatarios. Esta persona no podrá descifrar el mensaje si lo cifra.
- TM [partial]: You did not select encryption keys for some of the recipients; these persons will not be able to decrypt the message if you encrypt it. → No ha seleccionado clave de cifrado para algunos de los destinatarios del mensaje. Si cifra el mensaje, esas personas no podrán descifrarlo.
- TM [partial]: You did not select an encryption key for any of the recipients of this message; therefore, the message will not be encrypted. → No seleccionó una clave de cifrado para alguno de los destinatarios de este mensaje. Por lo tanto, el mensaje no se cifrará.

### K79c36708f4d3:de (KDE4/de, band <50, fuzzy 46) ΔKiwi -0.034

- **Source:** The pre shared key could not be found, check PSK settings.
- **Zero-shot:** Der vorab gemeinsame Schlüssel (PSK) konnte nicht gefunden werden; bitte prüfen Sie die PSK-Einstellungen.
- **semantic_ctx:** Der Preshared-Schlüssel konnte nicht gefunden werden, überprüfen Sie die PSK-Einstellungen.
- **Reference (not shown to any system or evaluator):** Datei mit dem privaten Schlüssel (%1) kann nicht gefunden werden. Bitte PSK-Einstellungen prüfen.
- TM [style_convention]: Your secret key could not be exported. Check the key. → Ihr geheimer Schlüssel kann nicht exportiert werden. Überprüfen Sie den Schlüssel.
- TM [terminology]: Pre-shared key for authentication (shared secret) → Pre shared-Schlüssel für Authentisierung (shared secret)
- TM [terminology]: Pre shared key file → Preshared-Schlüsseldatei

## semantic_ctx: Improvements

### Ka43608cada29:de (KDE4/de, band 75-84, fuzzy 80) ΔKiwi +0.173

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** Geometrisch - Einkerbung Pfeil links
- **semantic_ctx:** Geometrie - Eingekerbter Pfeil nach links
- **Reference (not shown to any system or evaluator):** Geometrie - Eingekerbter Pfeil nach linksStencils
- TM [partial]: Geometric - Notched Right Arrow → Geometrie - Eingekerbter Pfeil nach rechtsStencils
- TM [terminology]: Geometric - Left-Right Arrow → Geometrie - Pfeil nach links und rechtsStencils
- TM [terminology]: Geometric - Left-Right-Up Arrow → Geometrie - Pfeil nach links, rechts und obenStencils

### E8925bc1668d3:es (EMEA/es, band 50-74, fuzzy 71) ΔKiwi +0.044

- **Source:** Patients receiving VIRACEPT TID (n=11) achieved nelfinavir peak plasma concentrations (Cmax) of 3.0 ± 1.6 µg/ml and morning and evening trough concentrations of 1.4 ± 0.6 µg/ml and 1.0 ± 0.5 µg/ml, respectively.
- **Zero-shot:** Los pacientes que recibieron VIRACEPT tres veces al día (n=11) alcanzaron concentraciones plasmáticas máximas (Cmax) de nelfinavir de 3,0 ± 1,6 µg/ml y concentraciones valle matutinas y vespertinas de 1,4 ± 0,6 µg/ml y 1,0 ± 0,5 µg/ml, respectivamente.
- **semantic_ctx:** Los pacientes que recibían VIRACEPT TID (n = 11) alcanzaron concentraciones plasmáticas máximas (Cmax) de nelfinavir de 3,0 ± 1,6 µg/ml y concentraciones mínimas por la mañana y por la noche de 1,4 ± 0,6 µg/ml y 1,0 ± 0,5 µg/ml, respectivamente.
- **Reference (not shown to any system or evaluator):** Los pacientes que recibieron VIRACEPT TID (n=11) alcanzaron concentraciones máximas en plasma (Cmax) de 3,0 ± 1,6 µg/ml y concentraciones mínimas por la mañana y por la noche de 1,4 ± 0,6 µg/ml y 1,0 ± 0,5 µg/ml, respectivamente.
- TM [partial]: Patients receiving VIRACEPT BID (n=10) achieved nelfinavir Cmax of 4.0 ± 0.8 µg/ml and morning and evening trough concentrations of 2.2 ± 1.3 µg/ml and 0.7 ± 0.4 µg/ml, respectively. → Los pacientes que recibían VIRACEPT BID (n = 10) alcanzaron una Cmax de nelfinavir de 4,0±0,8 µg/ml y concentraciones mínimas por la mañana y por la noche de 2,2±1,3 µg/ml y 0,7±0,4 µg/ml, respectivamente.
- TM [none]: After infusion of 1,500 mg/ m2 nelarabine over two hours in adult patients, mean (%CV) plasma nelarabine Cmax and AUCinf values were 13.9 µM (81%) and 13.5 µM. h (56%) respectively. → Tras la perfusión de 1.500 mg/ m2 de nelarabina durante unas dos horas en adultos, la media (%CV) de los valores de Cmax y AUCinf de nelarabina en plasma fueron 13,9 µM (81%) y 13,5 µM. h (56%) respectivamente.
- TM [partial]: Following a dosage regimen of 800 mg every 8 hours, measured peak plasma concentrations (Cmax) after morning, afternoon and evening doses were 15,550 nM, 8,720 nM and 8,880 nM, respectively. → Después de una pauta posológica de 800 mg cada 8 horas, las concentraciones plasmáticas máximas (Cmax) medidas después de las dosis de la mañana, tarde y noche fueron de 15.550 nM, 8.720 nM y 8.880 nM, respectivamente.

### K692786e06f39:zh_CN (KDE4/zh_CN, band 85-94, fuzzy 90) ΔKiwi +0.036

- **Source:** The requested device could not be initialized ("mounted"). The reported error was: %1
- **Zero-shot:** 无法初始化（“挂载”）请求的设备。报告的错误为：%1
- **semantic_ctx:** 请求的设备无法被初始化（“挂载”）。报告的错误为：%1
- **Reference (not shown to any system or evaluator):** 请求的设备无法被初始化 (“ 被挂载 ”) 。 报告的错误是 ：% 1
- TM [misleading]: The requested device could not be uninitialized ("unmounted"). The reported error was: %1 → 请求的设备无法被卸载。 报告的错误是 ：% 1
- TM [partial]: Could not mount device. The reported error was: %1 → 无法挂载设备 。 报告的错误为 ：% 1
- TM [misleading]: Could not unmount device. The reported error was: %1 → 无法卸载设备 。 报告的错误为 ：% 1

### Kaa5339f3ff22:zh_CN (KDE4/zh_CN, band 100, fuzzy 100) ΔKiwi +0.012

- **Source:** Find text Shows a dialog that allows you to find text on the displayed page.
- **Zero-shot:** 查找文本 显示一个允许您在当前显示页面中查找文本的对话框。
- **semantic_ctx:** 查找文本 显示一个对话框，让您可以在所显示的页面中查找文本。
- **Reference (not shown to any system or evaluator):** 查找文本 将显示一个让您在所显示页面中查找文本的对话框 。 @ title: menu HTML frame/ iframe
- TM [full]: Find text Shows a dialog that allows you to find text on the displayed page. → 查找文本 显示一个对话框， 让您可以在所显示的页面中查找文本 。
- TM [terminology]: Shows a list of strings to search for (and if you specified it, a list of strings to replace with). Use the "add strings" dialog to edit your string list or double click on a string. → 显示搜索字符串列表( 如果您明确要求， 则由指定字符串替换显示) 。 使用“ 添加字符串” 对话框可编辑您的字符串列表， 或者双击字符串也可执行操作 。
- TM [terminology]: Search for text within the presentation. → 在演示文稿中搜索文本 。

### K7ede7068b57a:zh_CN (KDE4/zh_CN, band 95-99, fuzzy 96) ΔKiwi +0.006

- **Source:** You did not select an encryption key for one of the recipients; this person will not be able to decrypt the message if you encrypt it.
- **Zero-shot:** 您未为其中一名收件人选择加密密钥；如果您对其进行加密，该人员将无法解密此消息。
- **semantic_ctx:** 您没有为其中一名收件人选择加密密钥；如果您加密此信件，该收件人将无法解密。
- **Reference (not shown to any system or evaluator):** 您没有选择给该信件收件人其中之一的加密密钥， 如果您加密此信件， 此收件人无法将其解密 。
- TM [full]: You did not select an encryption key for one of the recipients: this person will not be able to decrypt the message if you encrypt it. → 您没有为此信件的收件人之一选择加密密钥； 因此， 如果您加密的话， 该收件人将无法解密此信件 。
- TM [partial]: You did not select encryption keys for some of the recipients; these persons will not be able to decrypt the message if you encrypt it. → 您没有选择给一部分收件人的加密密钥， 如果您加密此信件， 这些人无法将其解密 。
- TM [partial]: You did not select an encryption key for any of the recipients of this message; therefore, the message will not be encrypted. → 您没有为此信件的任何一个收件人选择加密密钥； 因此， 无法加密此信件 。

### K0ae48fe4cc74:de (KDE4/de, band 100, fuzzy 100) ΔKiwi +0.005

- **Source:** Create a new journal
- **Zero-shot:** Neues Tagebuch erstellen
- **semantic_ctx:** Ein neues Journal erstellen
- **Reference (not shown to any system or evaluator):** Ein neues Journal hinzufügen
- TM [full]: Create a new journal → Ein neues Journal erstellen@info:whatsthis
- TM [partial]: Create a new project → Neues Projekt erstellen
- TM [partial]: Create a new document → Neues Dokument erstellen

## fuzzy_ctx: Degradations

### Ka43608cada29:es (KDE4/es, band 75-84, fuzzy 80) ΔKiwi -0.166

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** Geométrico - Flecha izquierda con muesca
- **fuzzy_ctx:** Geometría - Flecha izquierda irregular
- **Reference (not shown to any system or evaluator):** Geometría - Flecha izquierda irregularStencils
- TM [partial]: Geometric - Notched Right Arrow → Geometría - Flecha derecha irregularStencils
- TM [terminology]: Geometric - Up Arrow → Geometría - Flecha arribaStencils
- TM [terminology]: Geometric - Up-Down-Left Arrow → Geometría - Flecha arriba-abajo-izquierdaStencils

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

### K692786e06f39:es (KDE4/es, band 85-94, fuzzy 90) ΔKiwi -0.060

- **Source:** The requested device could not be initialized ("mounted"). The reported error was: %1
- **Zero-shot:** No se pudo inicializar ("montar") el dispositivo solicitado. El error reportado fue: %1
- **fuzzy_ctx:** El dispositivo solicitado no se pudo desinicializar («montar»). El error emitido fue: %1
- **Reference (not shown to any system or evaluator):** El dispositivo solicitado no se pudo inicializar (« montar »). El error emitido fue: %1
- TM [partial]: The requested device could not be uninitialized ("unmounted"). The reported error was: %1 → El dispositivo solicitado no se pudo desinicializar (« desmontar »). El error emitido fue: %1
- TM [misleading]: Could not unmount device. The reported error was: %1 → No se pudo desmontar el dispositivo. El mensaje de error fue: %1
- TM [partial]: Could not mount device. The reported error was: %1 → No se pudo montar el dispositivo. El mensaje de error fue: %1

### K7ede7068b57a:es (KDE4/es, band 95-99, fuzzy 96) ΔKiwi -0.038

- **Source:** You did not select an encryption key for one of the recipients; this person will not be able to decrypt the message if you encrypt it.
- **Zero-shot:** No ha seleccionado una clave de cifrado para uno de los destinatarios; esta persona no podrá descifrar el mensaje si lo cifra.
- **fuzzy_ctx:** No seleccionó una clave de cifrado para uno de los destinatarios; esta persona no podrá descifrar el mensaje si lo cifra.
- **Reference (not shown to any system or evaluator):** No ha seleccionado una clave de cifrado para uno de los destinatarios. Si cifra el mensaje, esa persona no podrá descifrarlo.
- TM [full]: You did not select an encryption key for one of the recipients: this person will not be able to decrypt the message if you encrypt it. → No seleccionó una clave de cifrado para alguno de los destinatarios. Esta persona no podrá descifrar el mensaje si lo cifra.
- TM [partial]: You did not select encryption keys for some of the recipients; these persons will not be able to decrypt the message if you encrypt it. → No ha seleccionado clave de cifrado para algunos de los destinatarios del mensaje. Si cifra el mensaje, esas personas no podrán descifrarlo.
- TM [partial]: You did not select an encryption key for any of the recipients of this message; therefore, the message will not be encrypted. → No seleccionó una clave de cifrado para alguno de los destinatarios de este mensaje. Por lo tanto, el mensaje no se cifrará.

### Kd2585fdc51e4:zh_CN (KDE4/zh_CN, band 75-84, fuzzy 75) ΔKiwi -0.032

- **Source:** Santa Cruz del Quiché
- **Zero-shot:** 圣克鲁斯-德尔基切
- **fuzzy_ctx:** 圣克鲁斯-德基切
- **Reference (not shown to any system or evaluator):** 圣克鲁斯guatemala. kgm
- TM [terminology]: Santa Cruz del Seibo → 圣克鲁兹赛博dominican_ republic. kgm
- TM [terminology]: Santa Cruz de Tenerife → 圣克鲁斯- 德特内里费spain_ provinces. kgm
- TM [partial]: Santa Cruz de Barahona → 圣克鲁斯德巴拉奥纳dominican_ republic. kgm

## fuzzy_ctx: Improvements

### Ka43608cada29:de (KDE4/de, band 75-84, fuzzy 80) ΔKiwi +0.173

- **Source:** Geometric - Notched Left Arrow
- **Zero-shot:** Geometrisch - Einkerbung Pfeil links
- **fuzzy_ctx:** Geometrie - Eingekerbter Pfeil nach links
- **Reference (not shown to any system or evaluator):** Geometrie - Eingekerbter Pfeil nach linksStencils
- TM [partial]: Geometric - Notched Right Arrow → Geometrie - Eingekerbter Pfeil nach rechtsStencils
- TM [partial]: Geometric - Up Arrow → Geometrie - Pfeil nach obenStencils
- TM [terminology]: Geometric - Up-Down-Left Arrow → Geometrie - Pfeil nach oben, unten und linksStencils

### E8925bc1668d3:es (EMEA/es, band 50-74, fuzzy 71) ΔKiwi +0.044

- **Source:** Patients receiving VIRACEPT TID (n=11) achieved nelfinavir peak plasma concentrations (Cmax) of 3.0 ± 1.6 µg/ml and morning and evening trough concentrations of 1.4 ± 0.6 µg/ml and 1.0 ± 0.5 µg/ml, respectively.
- **Zero-shot:** Los pacientes que recibieron VIRACEPT tres veces al día (n=11) alcanzaron concentraciones plasmáticas máximas (Cmax) de nelfinavir de 3,0 ± 1,6 µg/ml y concentraciones valle matutinas y vespertinas de 1,4 ± 0,6 µg/ml y 1,0 ± 0,5 µg/ml, respectivamente.
- **fuzzy_ctx:** Los pacientes que recibían VIRACEPT TID (n = 11) alcanzaron concentraciones plasmáticas máximas (Cmax) de nelfinavir de 3,0 ± 1,6 µg/ml y concentraciones mínimas por la mañana y por la noche de 1,4 ± 0,6 µg/ml y 1,0 ± 0,5 µg/ml, respectivamente.
- **Reference (not shown to any system or evaluator):** Los pacientes que recibieron VIRACEPT TID (n=11) alcanzaron concentraciones máximas en plasma (Cmax) de 3,0 ± 1,6 µg/ml y concentraciones mínimas por la mañana y por la noche de 1,4 ± 0,6 µg/ml y 1,0 ± 0,5 µg/ml, respectivamente.
- TM [partial]: Patients receiving VIRACEPT BID (n=10) achieved nelfinavir Cmax of 4.0 ± 0.8 µg/ml and morning and evening trough concentrations of 2.2 ± 1.3 µg/ml and 0.7 ± 0.4 µg/ml, respectively. → Los pacientes que recibían VIRACEPT BID (n = 10) alcanzaron una Cmax de nelfinavir de 4,0±0,8 µg/ml y concentraciones mínimas por la mañana y por la noche de 2,2±1,3 µg/ml y 0,7±0,4 µg/ml, respectivamente.
- TM [terminology]: Cmax was 1.6±0.36 microgram/ ml and 1.4±0.22 microgram/ ml on Days 1 and 3, respectively. → La Cmax fue 1,6±0,36 microgramos/ ml y 1,4±0,22 microgramos/ ml los días 1 y 3, respectivamente.
- TM [style_convention]: Following a single oral dose of cysteamine bitartrate equivalent to 1.05 g of cysteamine free base in healthy volunteers, the mean (± sd) values for the time to peak and peak plasma concentration are 1.4 (± 0.5) hours and 4.0 (± 1.0) µg/ ml, respectively. → Después de una dosis oral única de bitartrato de cisteamina equivalente a 1,05 g de base libre de cisteamina en voluntarios sanos, las medias (± DE) del tiempo hasta la concentración máxima y de la concentración plasmática máxima son de 1,4 (± 0,5) horas y 4,0 (± 1,0) µg/ ml, respectivamente.

### K692786e06f39:zh_CN (KDE4/zh_CN, band 85-94, fuzzy 90) ΔKiwi +0.036

- **Source:** The requested device could not be initialized ("mounted"). The reported error was: %1
- **Zero-shot:** 无法初始化（“挂载”）请求的设备。报告的错误为：%1
- **fuzzy_ctx:** 请求的设备无法被初始化（“挂载”）。报告的错误为：%1
- **Reference (not shown to any system or evaluator):** 请求的设备无法被初始化 (“ 被挂载 ”) 。 报告的错误是 ：% 1
- TM [misleading]: The requested device could not be uninitialized ("unmounted"). The reported error was: %1 → 请求的设备无法被卸载。 报告的错误是 ：% 1
- TM [misleading]: Could not unmount device. The reported error was: %1 → 无法卸载设备 。 报告的错误为 ：% 1
- TM [partial]: Could not mount device. The reported error was: %1 → 无法挂载设备 。 报告的错误为 ：% 1

### Kaa5339f3ff22:zh_CN (KDE4/zh_CN, band 100, fuzzy 100) ΔKiwi +0.012

- **Source:** Find text Shows a dialog that allows you to find text on the displayed page.
- **Zero-shot:** 查找文本 显示一个允许您在当前显示页面中查找文本的对话框。
- **fuzzy_ctx:** 查找文本 显示一个对话框，让您可以在所显示的页面中查找文本。
- **Reference (not shown to any system or evaluator):** 查找文本 将显示一个让您在所显示页面中查找文本的对话框 。 @ title: menu HTML frame/ iframe
- TM [full]: Find text Shows a dialog that allows you to find text on the displayed page. → 查找文本 显示一个对话框， 让您可以在所显示的页面中查找文本 。
- TM [terminology]: The Next button presents a dialog box that allows you to change the name used on the HTML page for each slide: → 下一步 将打开的对话框允许您更改每张幻灯片的名称 。
- TM [partial]: Configure Notifications Shows a dialog that lets you configure notifications. → 配置通知 显示一个让您配置通知的对话框 。

### K79c36708f4d3:de (KDE4/de, band <50, fuzzy 46) ΔKiwi +0.009

- **Source:** The pre shared key could not be found, check PSK settings.
- **Zero-shot:** Der vorab gemeinsame Schlüssel (PSK) konnte nicht gefunden werden; bitte prüfen Sie die PSK-Einstellungen.
- **fuzzy_ctx:** Der vorab gemeinsam genutzte Schlüssel konnte nicht gefunden werden; bitte überprüfen Sie die PSK-Einstellungen.
- **Reference (not shown to any system or evaluator):** Datei mit dem privaten Schlüssel (%1) kann nicht gefunden werden. Bitte PSK-Einstellungen prüfen.
- TM [style_convention]: The executable %1 could not be found in your PATH. → Die ausführbare Datei %1 ist über Ihren PATH nicht auffindbar.
- TM [partial]: The selected engine could not be found. Please reinstall KMobileTools. → Der ausgewählte Treiber konnte nicht gefunden werden. Bitte KMobileTools erneut installieren.
- TM [style_convention]: Your secret key could not be exported. Check the key. → Ihr geheimer Schlüssel kann nicht exportiert werden. Überprüfen Sie den Schlüssel.

### K7ede7068b57a:zh_CN (KDE4/zh_CN, band 95-99, fuzzy 96) ΔKiwi +0.006

- **Source:** You did not select an encryption key for one of the recipients; this person will not be able to decrypt the message if you encrypt it.
- **Zero-shot:** 您未为其中一名收件人选择加密密钥；如果您对其进行加密，该人员将无法解密此消息。
- **fuzzy_ctx:** 您没有为其中一名收件人选择加密密钥；如果您加密此信件，该收件人将无法解密。
- **Reference (not shown to any system or evaluator):** 您没有选择给该信件收件人其中之一的加密密钥， 如果您加密此信件， 此收件人无法将其解密 。
- TM [full]: You did not select an encryption key for one of the recipients: this person will not be able to decrypt the message if you encrypt it. → 您没有为此信件的收件人之一选择加密密钥； 因此， 如果您加密的话， 该收件人将无法解密此信件 。
- TM [partial]: You did not select encryption keys for some of the recipients; these persons will not be able to decrypt the message if you encrypt it. → 您没有选择给一部分收件人的加密密钥， 如果您加密此信件， 这些人无法将其解密 。
- TM [partial]: You did not select an encryption key for any of the recipients of this message; therefore, the message will not be encrypted. → 您没有为此信件的任何一个收件人选择加密密钥； 因此， 无法加密此信件 。
