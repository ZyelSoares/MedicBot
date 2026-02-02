# Como usar as logos no MedicBot (Tkinter) – Passo a passo

Você já tem os PNG na pasta `Medic Logo`. O que falta é o **código** carregar e exibir essas imagens.

---

## 1. Onde estão as imagens

Estrutura:

```
conversa/
├── medicbot.py
├── Medic Logo/
│   ├── Logo+nome do lado.png    → header (barra de cima)
│   ├── Logo+Nome abaixo.png     → página Sobre
│   └── Só Logo PNG.png          → ícone da janela (e sidebar, se quiser)
```

O programa descobre a pasta do script com `obter_pasta_script()`. Assim funciona tanto rodando o `.py` quanto o `.exe` (PyInstaller).

---

## 2. Como o Tkinter exibe imagens

### 2.1 Objeto que representa a imagem: `PhotoImage`

No Tkinter, você não coloca o arquivo direto na tela. Você:

1. **Carrega** o arquivo e vira um objeto `PhotoImage`.
2. **Guarda** esse objeto em uma variável (ex.: `self.logo_header`). Se não guardar, o Python pode apagar a imagem da memória e ela some da tela.
3. **Usa** esse objeto em um `Label` ou no `Canvas`.

Exemplo mínimo:

```python
from tkinter import tk, PhotoImage

root = tk.Tk()
# Carregar PNG (no Windows, PhotoImage suporta PNG)
img = PhotoImage(file="Medic Logo/Logo+nome do lado.png")
# Guardar referência!
self.minha_logo = img
# Mostrar num Label
lbl = tk.Label(root, image=img)
lbl.pack()
root.mainloop()
```

Se você fizer `Label(..., image=img)` mas não guardar `img` em `self.alguma_coisa`, a imagem pode sumir. Por isso no MedicBot vamos usar `self.logo_header`, `self.logo_icon`, etc.

### 2.2 Redimensionar (opcional)

`PhotoImage` não redimensiona sozinho. Se precisar de tamanho menor (ex.: ícone 32x32):

- **Opção A:** Usar **Pillow (PIL)** para abrir o PNG, redimensionar e aí converter para `PhotoImage`. Exemplo:

```python
from PIL import Image, ImageTk
img_pil = Image.open("Só Logo PNG.png").resize((32, 32))
img_tk = ImageTk.PhotoImage(img_pil)
# Guardar: self.icon_32 = img_tk
```

- **Opção B:** Deixar a imagem no tamanho original. Para header e Sobre costuma ficar bom.

No MedicBot vamos usar tamanhos que combinem com o layout; se quiser ícone pequeno, dá para adicionar Pillow depois.

---

## 3. Onde cada logo entra no código

| Logo                 | Arquivo                   | Onde no medicbot.py                          |
|----------------------|---------------------------|----------------------------------------------|
| Logo + nome de lado  | `Logo+nome do lado.png`   | Header: onde hoje está o texto "MedicBot"   |
| Logo + nome abaixo   | `Logo+Nome abaixo.png`    | Página Sobre: onde está o título "MedicBot"  |
| Só logo              | `Só Logo PNG.png`         | Ícone da janela (`root.iconphoto`)           |

Resumo do que o código faz:

1. **Caminho das imagens**  
   `pasta = obter_pasta_script()` → `os.path.join(pasta, "Medic Logo", "Nome do arquivo.png")`.

2. **Carregar com tratamento de erro**  
   `try: img = tk.PhotoImage(file=caminho)` e guardar em `self.logo_header` (ou `self.logo_sobre`, `self.logo_icon`). Se der erro (arquivo não existe ou Tk antigo), não quebra o programa: continua com o texto "MedicBot".

3. **Header**  
   Em vez de um `Label` com `text="MedicBot"`, usar um `Label` com `image=self.logo_header`. Se `self.logo_header` for `None`, manter o `Label` de texto.

4. **Sobre**  
   Mesma ideia: `Label` com `image=self.logo_sobre` no topo da página Sobre; se não tiver imagem, manter o texto.

5. **Ícone da janela**  
   `self.root.iconphoto(True, self.logo_icon)` no início. Só chama se `self.logo_icon` tiver sido carregado.

Assim você “conecta” os PNG que já tem à interface, sem precisar mexer nas imagens de novo.

---

## 4. Resumo técnico

- **Carregar:** `tk.PhotoImage(file=caminho_completo)`.
- **Manter na tela:** guardar o retorno em `self.alguma_variavel`.
- **Mostrar:** `Label(master, image=self.alguma_variavel)` ou `Canvas.create_image(..., image=...)`.
- **Ícone da janela:** `root.iconphoto(True, self.logo_icon)`.
- **Pasta das imagens:** `os.path.join(obter_pasta_script(), "Medic Logo", "arquivo.png")`.

Se um dia quiser redimensionar (ex.: ícone pequeno), aí sim vale usar Pillow e `ImageTk.PhotoImage` como no exemplo acima.
