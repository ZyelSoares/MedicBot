# MedicBot – Robô de Manutenção do Computador

**Médico + Bot**: programa com interface verde para manter o PC rápido e limpo. Escolha quais etapas executar e rode a manutenção com um clique.

---

## Instalação passo a passo

Para o guia completo com logo e instruções detalhadas, abra:

**[INSTALACAO.md](INSTALACAO.md)** – Passo a passo bonitinho com logo, requisitos e dicas.

---

## Ver a interface (como um “npm run dev”)

O MedicBot é um **programa de janela** (Python + tkinter), não um site. Para ver a interface:

1. **Opção fácil**: dê **dois cliques** em **`Rodar_MedicBot.bat`**  
   → Abre a janela do MedicBot com a paleta verde.

2. **Pelo terminal**: na pasta do projeto, execute:
   ```bash
   python medicbot.py
   ```
   → A janela abre na hora. Não usa `npm`; é só `python medicbot.py`.

**Requisito**: ter [Python](https://www.python.org/downloads/) instalado no PC (geralmente já vem ou você instala uma vez).

---

## Subir atualizações (setup e ship)

Para o programa, o fluxo é parecido com o de um site:

| No site | No MedicBot |
|--------|--------------|
| `npm run setup` | `npm run setup` (instala dependências, inclusive PyInstaller) |
| `npm run ship` | `npm run ship` (gera o .exe para distribuir) |

**Na pasta do projeto**, no terminal:

1. **Primeira vez (ou depois de clonar):**
   ```bash
   npm run setup
   ```
   Instala o que está em `requirements.txt` (incluindo PyInstaller).

2. **Gerar a versão para distribuir:**
   ```bash
   npm run ship
   ```
   Roda o PyInstaller e gera o **.exe** na pasta **`dist/`** (arquivo **`MedicBot.exe`**). Você pode enviar esse .exe ou a pasta `dist/` para quem for usar.

**Observação:** não precisa ter Node/npm instalado para rodar o MedicBot (só Python). O `package.json` existe para você usar `npm run setup` e `npm run ship` como comandos. Se preferir sem npm: `pip install -r requirements.txt` e depois `pyinstaller medicbot.spec`.

---

## O que o MedicBot faz (14 etapas)

| # | Tarefa | O que é |
|---|--------|--------|
| 1 | **Windows Temp** | Limpa `C:\Windows\Temp` (arquivos temporários do sistema) |
| 2 | **%TEMP%** | Limpa a pasta Temp do seu usuário (AppData\Local\Temp) |
| 3 | **Prefetch** | Limpa `C:\Windows\Prefetch` (cache de programas) |
| 4 | **MRT** | Abre a Ferramenta de Remoção de Software Mal-intencionado da Microsoft |
| 5 | **Antivírus** | Roda uma verificação **rápida** do Windows Defender |
| 6 | **Desfragmentação** | Otimiza todas as unidades fixas (HD/SSD) |
| 7 | **Lixeira** | Esvazia a Lixeira |
| 8 | **Limpeza do Sistema (DISM)** | Remove atualizações antigas do Windows (Component Store) – libera bastante espaço |
| 9 | **Limpeza de Disco** | Abre o **cleanmgr** para você usar “Limpar arquivos do sistema” e outras opções |
| 10 | **Programas de inicialização** | Abre **Configurações > Inicialização** e lista no log os programas que iniciam com o Windows |
| 11 | **Cache DNS** | Limpa o cache DNS (`ipconfig /flushdns`) – ajuda na estabilidade da rede |
| 12 | **Cache de miniaturas** | Remove cache de miniaturas do Explorer (thumbcache) |
| 13 | **Relatórios de erro (WER)** | Limpa relatórios antigos do Windows Error Reporting |
| 14 | **Delivery Optimization** | Limpa cache de atualizações compartilhadas (Delivery Optimization) |

Tudo isso em uma única execução.

---

## Como usar

### Opção 1 – Pelo programa (interface verde, recomendado)

1. Abra o MedicBot: **dois cliques** em **`Rodar_MedicBot.bat`** ou execute `python medicbot.py`.
2. Na janela, marque as etapas que deseja e clique em **“Executar tudo”** ou **“Executar selecionados”**.
3. O Windows pede permissão de administrador; clique em **Sim**. A manutenção roda em outra janela (PowerShell). O log fica em **MedicBot_log.txt** na mesma pasta.

### Opção 2 – Só pelo script (sem interface)

1. Dê **dois cliques** em **`Executar_MediBot.bat`** (ou **`Executar_MedicBot.bat`** se existir).
2. Quando o Windows pedir permissão, clique em **Sim**.
3. O MedicBot roda todas as 14 etapas na janela do PowerShell e salva o log.

### Opção 3 – Pelo PowerShell (como administrador)

1. Clique com o **botão direito** no **Menu Iniciar** e escolha **“Terminal (Admin)”** ou **“Windows PowerShell (Administrador)”**.
2. Vá até a pasta do projeto:
   ```powershell
   cd "$env:USERPROFILE\Desktop\conversa"
   ```
3. Execute:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\MedicBot.ps1
   ```

---

## Detalhes importantes

- **Permissão de administrador**: o script **precisa** rodar como administrador. Use o `.bat` (que pede admin) ou abra o PowerShell como administrador.
- **MRT**: abre em uma janela separada. Você pode acompanhar e fechar quando terminar; o script continua depois.
- **Antivírus**: é feita uma **verificação rápida**. Para verificação completa, use depois o “Segurança do Windows” manualmente.
- **Limpeza de Disco (etapa 9)**: abre a janela do **Limpeza de Disco**. Clique em **“Limpar arquivos do sistema”** para liberar ainda mais espaço (arquivos de atualização antigos, etc.).
- **Programas de inicialização (etapa 10)**: abre **Configurações > Aplicativos > Inicialização**. Desative programas que não precisam abrir com o Windows para o PC ligar mais rápido.
- **DISM (etapa 8)**: pode levar alguns minutos e libera bastante espaço (atualizações antigas do Windows). É seguro.
- **Log**: ao final, o MedicBot grava **`MedicBot_log.txt`** na pasta do projeto, com o que foi feito e possíveis avisos/erros.
- **Cores**: interface em paleta verde (positivo, saúde, crescimento).

---

## Com que frequência usar

- **Temp + %TEMP% + Lixeira + DNS + miniaturas + WER + Delivery Optimization**: 1x por semana ou quando quiser.
- **Prefetch**: de vez em quando (ex.: 1x por mês).
- **MRT**: 1x por mês ou se suspeitar de algo estranho.
- **Defender**: o rápido pode ser 1x por semana; o completo 1x por mês.
- **Desfragmentação**: em HD, 1x por mês; em SSD o Windows costuma só fazer TRIM.
- **DISM + Limpeza de Disco**: 1x por mês (liberam bastante espaço).
- **Revisar programas de inicialização**: sempre que notar o PC lento ao ligar.

---

## Resumo

- **Interface**: **`Rodar_MedicBot.bat`** ou **`python medicbot.py`** para abrir o programa.
- **Executar manutenção**: pelo programa (Executar tudo / Executar selecionados) ou **`Executar_MediBot.bat`** para rodar tudo direto.
- **Sem custo**: só usa ferramentas do próprio Windows.
- **Log**: `MedicBot_log.txt` na pasta do projeto.

Se quiser mais “consultas” no MedicBot (por exemplo: ver uso de disco, desativar efeitos visuais, etc.), é só pedir.
