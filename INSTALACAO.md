# MedicBot – Passo a passo da instalação

![MedicBot](Medic%20Logo/Logo%2BNome%20abaixo.png)

**Médico + Bot** – Manutenção do seu PC com um clique.

---

## Passo 1: Baixar o MedicBot

- Se você recebeu uma pasta **`conversa`** ou **`MedicBot`**, ela já contém tudo.
- Se recebeu um arquivo **`.zip`**, extraia-o em uma pasta (ex.: `C:\MedicBot` ou na Área de Trabalho).

---

## Passo 2: Instalar o Python (primeira vez no PC)

O MedicBot precisa do **Python** para rodar.

1. Acesse [python.org/downloads](https://www.python.org/downloads/).
2. Baixe a versão mais recente (ex.: Python 3.12).
3. Ao instalar, **marque a opção**:
   - ☑️ **"Add Python to PATH"** (Adicionar Python ao PATH)
4. Clique em **"Install Now"** e aguarde terminar.

> Se você já usa Python no PC, pode pular este passo.

---

## Passo 3: Instalar as dependências

1. Abra o **Prompt de Comando** ou o **PowerShell**.
2. Vá até a pasta do MedicBot:
   ```bash
   cd C:\caminho\para\pasta\conversa
   ```
   *(troque pelo caminho real da pasta)*

3. Execute:
   ```bash
   pip install -r requirements.txt
   ```
   Ou, se tiver npm:
   ```bash
   npm run setup
   ```

---

## Passo 4: Executar o MedicBot

### Opção fácil (recomendado)

- Dê **dois cliques** em **`Rodar_MedicBot.bat`**  
→ A janela do MedicBot abre.

### Opção pelo terminal

```bash
python medicbot.py
```

---

## Passo 5: Rodar como Administrador (importante)

Para as etapas de manutenção funcionarem, o MedicBot precisa de **permissão de administrador**:

1. **Clique com o botão direito** no atalho ou no `Rodar_MedicBot.bat`.
2. Escolha **"Executar como administrador"**.
3. Quando o Windows perguntar, clique em **Sim**.

Ou crie um atalho na Área de Trabalho e configure-o para **sempre** abrir como administrador.

---

## Gerar o .exe (opcional)

Se quiser um arquivo **`MedicBot.exe`** para enviar para outras pessoas:

```bash
npm run ship
```

O arquivo será criado em **`dist/MedicBot.exe`**.

---

## Resumo

| Passo | O que fazer |
|-------|-------------|
| 1 | Baixar e extrair a pasta do MedicBot |
| 2 | Instalar Python (com "Add to PATH") |
| 3 | Rodar `pip install -r requirements.txt` na pasta |
| 4 | Abrir com `Rodar_MedicBot.bat` ou `python medicbot.py` |
| 5 | Executar sempre **como Administrador** |

---

*Desenvolvido por Josiel de Araújo Soares*
