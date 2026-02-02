# MedicBot - Programa de Manutenção do Computador
# Interface estilo Driver Booster: moderna, com anel animado e paleta verde.

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import os
import sys
import webbrowser
import math
import threading
import json
import re

# No Windows: esconder janela do processo (não abrir PowerShell)
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)


def _matar_arvore_processo(proc):
    """Encerra o processo e todos os filhos (evita cleanmgr etc. continuarem ao cancelar)."""
    if proc is None:
        return
    pid = getattr(proc, "pid", None)
    if pid is None:
        return
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                creationflags=CREATE_NO_WINDOW,
                timeout=5,
            )
        except Exception:
            proc.terminate()
    else:
        proc.terminate()

# Paleta escuro (padrão)
CORES_ESCURO = {
    "fundo_escuro": "#121212",
    "fundo_medio": "#1e1e1e",
    "fundo_sidebar": "#1a1a1a",
    "fundo_cartao": "#f5f5f5",
    "texto_escuro": "#333333",
    "botao": "#40916c",
    "botao_hover": "#52b788",
    "anel_brilho": "#52b788",
    "anel_dim": "#2d3d32",
    "destaque": "#40916c",
    "texto": "#ffffff",
    "texto_secundario": "#b0b0b0",
    "badge": "#2d6a4f",
    "botao_centro": "#e8e8e8",
    "borda_cartao": "#e0e0e0",
}
CORES = CORES_ESCURO  # compatibilidade

INSTAGRAM_MEDICBOT = "https://www.instagram.com/eu.josielsoares/?hl=pt-br"

# Idiomas: pt (BR), en, es
STRINGS = {
    "pt": {
        "menu_inicio": "INÍCIO",
        "menu_o_que_faz": "FUNÇÕES",
        "menu_log": "LOG",
        "menu_sobre": "SOBRE",
        "menu_config": "CONFIGURAÇÕES",
        "titulo_sobre": "O que cada etapa faz no seu PC",
        "titulo_log": "Log",
        "titulo_config": "Configurações",
        "selecione_etapas": "Selecione as etapas que deseja executar:",
        "status_etapas": "Status: {} etapa(s) selecionada(s)",
        "executar": "EXECUTAR",
        "executando": "EXECUTANDO",
        "cancelar": "  Cancelar  ",
        "abrir_pasta_log": "  Abrir pasta do log  ",
        "saiba_etapas": "Saiba o que cada etapa faz no seu PC",
        "confirmar_cancelar_titulo": "Confirmar cancelamento",
        "confirmar_cancelar_msg": "Certeza que deseja cancelar?",
        "confirmar_cancelar_dica": "O ideal é deixar a manutenção terminar para um resultado completo. Se cancelar, as etapas em andamento não serão concluídas.",
        "nao_mostrar_novamente": "Não mostrar esta confirmação novamente",
        "sim": "Sim",
        "nao": "Não",
        "tema": "Aparência",
        "tema_escuro": "Modo escuro",
        "tema_claro": "Modo claro",
        "titulo_cancelamento": "Cancelamento",
        "confirmar_ao_cancelar": "Perguntar antes de cancelar a manutenção",
        "idioma": "Idioma",
        "idioma_pt": "Português (BR)",
        "idioma_en": "English",
        "idioma_es": "Español",
        "sobre_tagline": "Médico + Bot • Manutenção do seu PC",
        "sobre_paragrafo": "O MedicBot foi criado para ajudar as pessoas a manter o computador sempre otimizado, sem precisar fazer cada tarefa uma por uma — o que pode ser cansativo e confuso. Com um só clique, você escolhe as etapas e deixa o programa cuidar do resto.\n\nDesenvolvido por Josiel de Araújo Soares.",
        "sobre_etapas": "14 etapas de limpeza e otimização: Temp, Prefetch, MRT, Defender, Desfragmentação, DISM, Limpeza de Disco, Inicialização, DNS, miniaturas, WER e mais.",
        "sobre_instagram": "Siga o Instagram do desenvolvedor do MedicBot",
        "sobre_botao_seguir": "  Seguir  ",
        "info_etapas_demoram": "Algumas etapas podem demorar mais: Antivírus, MRT, Limpeza de Disco, DISM e Desfragmentação. O tempo varia conforme a quantidade de arquivos no PC.",
    },
    "en": {
        "menu_inicio": "HOME",
        "menu_o_que_faz": "FUNCTIONS",
        "menu_log": "LOG",
        "menu_sobre": "ABOUT",
        "menu_config": "SETTINGS",
        "titulo_sobre": "What each step does",
        "titulo_log": "Log",
        "titulo_config": "Settings",
        "selecione_etapas": "Select the steps you want to run:",
        "status_etapas": "Status: {} step(s) selected",
        "executar": "RUN",
        "executando": "RUNNING",
        "cancelar": "  Cancel  ",
        "abrir_pasta_log": "  Open log folder  ",
        "saiba_etapas": "Learn what each step does",
        "confirmar_cancelar_titulo": "Confirm cancellation",
        "confirmar_cancelar_msg": "Are you sure you want to cancel?",
        "confirmar_cancelar_dica": "For best results, let the maintenance finish. If you cancel, steps in progress will not be completed.",
        "nao_mostrar_novamente": "Do not show this confirmation again",
        "sim": "Yes",
        "nao": "No",
        "tema": "Appearance",
        "tema_escuro": "Dark mode",
        "tema_claro": "Light mode",
        "titulo_cancelamento": "Cancellation",
        "confirmar_ao_cancelar": "Ask before canceling maintenance",
        "idioma": "Language",
        "idioma_pt": "Português (BR)",
        "idioma_en": "English",
        "idioma_es": "Español",
        "sobre_tagline": "Doctor + Bot • Your PC Maintenance",
        "sobre_paragrafo": "MedicBot was created to help people keep their computer optimized without having to do each task one by one — which can be tedious and confusing. With one click, you choose the steps and let the program do the rest.\n\nDeveloped by Josiel de Araújo Soares.",
        "sobre_etapas": "14 cleaning and optimization steps: Temp, Prefetch, MRT, Defender, Defragmentation, DISM, Disk Cleanup, Startup, DNS, thumbnails, WER and more.",
        "sobre_instagram": "Follow the MedicBot developer on Instagram",
        "sobre_botao_seguir": "  Follow  ",
        "info_etapas_demoram": "Some steps may take longer: Antivirus, MRT, Disk Cleanup, DISM and Defragmentation. Time varies depending on how many files are on your PC.",
    },
    "es": {
        "menu_inicio": "INICIO",
        "menu_o_que_faz": "FUNCIONES",
        "menu_log": "REGISTRO",
        "menu_sobre": "ACERCA DE",
        "titulo_config": "Configuración",
        "titulo_sobre": "Qué hace cada paso",
        "titulo_log": "Registro",
        "menu_config": "CONFIGURACIÓN",
        "selecione_etapas": "Seleccione los pasos que desea ejecutar:",
        "status_etapas": "Estado: {} paso(s) seleccionado(s)",
        "executar": "EJECUTAR",
        "executando": "EJECUTANDO",
        "cancelar": "  Cancelar  ",
        "abrir_pasta_log": "  Abrir carpeta del registro  ",
        "saiba_etapas": "Sepa qué hace cada paso",
        "confirmar_cancelar_titulo": "Confirmar cancelación",
        "confirmar_cancelar_msg": "¿Está seguro de que desea cancelar?",
        "confirmar_cancelar_dica": "Lo mejor es dejar que el mantenimiento termine para un resultado completo. Si cancela, los pasos en curso no se completarán.",
        "nao_mostrar_novamente": "No mostrar esta confirmación de nuevo",
        "sim": "Sí",
        "nao": "No",
        "tema": "Apariencia",
        "tema_escuro": "Modo oscuro",
        "tema_claro": "Modo claro",
        "titulo_cancelamento": "Cancelación",
        "confirmar_ao_cancelar": "Preguntar antes de cancelar el mantenimiento",
        "idioma": "Idioma",
        "idioma_pt": "Português (BR)",
        "idioma_en": "English",
        "idioma_es": "Español",
        "sobre_tagline": "Médico + Bot • Mantenimiento de tu PC",
        "sobre_paragrafo": "MedicBot fue creado para ayudar a las personas a mantener su computadora optimizada sin tener que hacer cada tarea una por una — lo cual puede ser tedioso y confuso. Con un solo clic, eliges los pasos y el programa hace el resto.\n\nDesarrollado por Josiel de Araújo Soares.",
        "sobre_etapas": "14 pasos de limpieza y optimización: Temp, Prefetch, MRT, Defender, Desfragmentación, DISM, Limpieza de disco, Inicio, DNS, miniaturas, WER y más.",
        "sobre_instagram": "Sigue al desarrollador de MedicBot en Instagram",
        "sobre_botao_seguir": "  Seguir  ",
        "info_etapas_demoram": "Algunas etapas pueden tardar más: Antivirus, MRT, Limpieza de disco, DISM y Desfragmentación. El tiempo varía según la cantidad de archivos en el PC.",
    },
}

# Grupos para os cards: Limpeza (1,2,3,7,11,12,13,14) e Sistema (4,5,6,8,9,10)
ETAPAS_LIMPEZA = {1, 2, 3, 7, 11, 12, 13, 14}
ETAPAS_SISTEMA = {4, 5, 6, 8, 9, 10}

# Nomes curtos para os checkboxes na tela inicial
ETAPAS_SHORT = [
    "Windows Temp", "%TEMP%", "Prefetch", "MRT", "Antivírus Windows", "Desfragmentar",
    "Lixeira", "DISM", "Limpeza de Disco", "Inicialização", "DNS",
    "Miniaturas", "WER", "Delivery Optimization",
]

# Para a página "O que cada etapa faz" – título + descrição
ETAPAS_DESCRICOES = [
    ("Windows Temp", "Limpa arquivos temporários do sistema em C:\\Windows\\Temp."),
    ("%TEMP% (Temp do usuário)", "Limpa a pasta Temp do seu usuário (AppData\\Local\\Temp)."),
    ("Prefetch", "Limpa o cache de programas em C:\\Windows\\Prefetch."),
    ("MRT (Microsoft)", "Abre a Ferramenta de Remoção de Software Mal-intencionado da Microsoft."),
    ("Antivírus Windows", "Executa verificação rápida ou completa do Antivírus Windows (Defender). Escolha na tela inicial."),
    ("Desfragmentação", "Otimiza as unidades (desfragmentação em HD, TRIM em SSD)."),
    ("Lixeira", "Esvazia a Lixeira do Windows."),
    ("Limpeza do Sistema (DISM)", "Remove atualizações antigas do Windows (Component Store); libera bastante espaço."),
    ("Limpeza de Disco", "Executa a Limpeza de Disco (cleanmgr) automaticamente em todas as unidades, sem abrir janela."),
    ("Programas de inicialização", "Desativa programas desnecessários da pasta Inicialização do usuário (preserva itens do Windows e Microsoft). Itens desativados são movidos para a pasta Startup_Desativados_MedicBot."),
    ("Cache DNS", "Limpa o cache DNS (ipconfig /flushdns) para maior estabilidade da rede."),
    ("Cache de miniaturas", "Remove o cache de miniaturas do Explorer (thumbcache)."),
    ("Relatórios de erro (WER)", "Limpa relatórios antigos do Windows Error Reporting."),
    ("Delivery Optimization", "Limpa o cache de atualizações compartilhadas (Delivery Optimization)."),
]


def obter_pasta_script():
    """Pasta do executável (ou do .py). Quando .exe (PyInstaller), dados ficam em _MEIPASS."""
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def obter_pasta_config():
    """Pasta onde gravar config (gravável). Na primeira execução não existe arquivo."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def carregar_config():
    """Retorna dict com steps (lista) e defender_scan (str "1" ou "2") ou None na primeira vez."""
    path = os.path.join(obter_pasta_config(), "medicbot_config.json")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d
    except Exception:
        return None


def carregar_etapas_salvas():
    """Retorna lista de etapas selecionadas (1-14) ou None na primeira vez (tudo desmarcado)."""
    cfg = carregar_config()
    if cfg is None:
        return None
    steps = cfg.get("steps", [])
    return [s for s in steps if 1 <= s <= 14]


def salvar_etapas(etapas, defender_scan_type=None):
    """Grava etapas e opcionalmente defender_scan_type ("1" ou "2"). Se defender_scan_type for None, mantém o já salvo."""
    path = os.path.join(obter_pasta_config(), "medicbot_config.json")
    try:
        d = carregar_config() or {}
        d["steps"] = etapas
        if defender_scan_type is not None:
            d["defender_scan"] = defender_scan_type
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=0)
    except Exception:
        pass


def salvar_config_geral(confirmar_cancelar=None, idioma=None):
    """Grava opções gerais (confirmar ao cancelar, idioma). None = não alterar."""
    path = os.path.join(obter_pasta_config(), "medicbot_config.json")
    try:
        d = carregar_config() or {}
        if confirmar_cancelar is not None:
            d["confirmar_ao_cancelar"] = bool(confirmar_cancelar)
        if idioma is not None:
            d["idioma"] = str(idioma) if idioma in ("pt", "en", "es") else "pt"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=0)
    except Exception:
        pass


def obter_caminho_engine():
    pasta = obter_pasta_script()
    for nome in ("MedicBot.ps1", "MediBot.ps1"):
        caminho = os.path.join(pasta, nome)
        if os.path.isfile(caminho):
            return caminho
    return os.path.join(pasta, "MedicBot.ps1")


def carregar_logo(pasta_base, nome_arquivo, redimensionar=None):
    """Carrega um PNG como PhotoImage. Guarde o retorno em self.xxx senão a imagem some.
    redimensionar: (largura_max,) ou (largura_max, altura_max) para reduzir. Retorna None se erro."""
    caminho = os.path.join(pasta_base, "Medic Logo", nome_arquivo)
    if not os.path.isfile(caminho):
        return None
    try:
        img = tk.PhotoImage(file=caminho)
        if redimensionar and len(redimensionar) >= 1:
            w, h = img.width(), img.height()
            w_max = redimensionar[0] if redimensionar[0] else w
            h_max = redimensionar[1] if len(redimensionar) >= 2 and redimensionar[1] else h
            fator_w = ((w + w_max - 1) // w_max) if w > w_max and w_max > 0 else 1
            fator_h = ((h + h_max - 1) // h_max) if h > h_max and h_max > 0 else 1
            fator = max(fator_w, fator_h, 1)
            if fator > 1:
                img = img.subsample(fator, fator)
        return img
    except Exception:
        return None


def executar_manutencao(steps=None, on_line=None, on_done=None, defender_scan_type="1"):
    """Roda a manutenção dentro do programa (sem abrir PowerShell).
    defender_scan_type: "1" = rápida, "2" = completa."""
    engine = obter_caminho_engine()
    if not os.path.isfile(engine):
        if on_done:
            on_done(-1)
        return False, f"Arquivo do motor não encontrado: {engine}", None
    pasta = obter_pasta_script()
    args = [
        "powershell", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden",
        "-File", engine, "-Silent", "-DefenderScanType", defender_scan_type,
    ]
    if steps:
        args.extend(["-Steps", ",".join(str(s) for s in steps)])

    try:
        proc = subprocess.Popen(
            args,
            cwd=pasta,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=CREATE_NO_WINDOW,
            text=True,
        )
    except Exception as e:
        if on_done:
            on_done(-1)
        return False, str(e), None

    def ler_saida():
        try:
            for line in proc.stdout:
                line = line.rstrip()
                if line and on_line:
                    on_line(line)
            proc.wait()
            if proc.stderr:
                err = proc.stderr.read()
                if err and on_line:
                    for line in err.rstrip().splitlines():
                        if line:
                            on_line(line)
        except Exception:
            pass
        try:
            rc = proc.returncode if hasattr(proc, 'returncode') else -1
            if on_done:
                on_done(rc)
        except Exception:
            pass

    threading.Thread(target=ler_saida, daemon=True).start()
    return True, None, proc


class MedicBotApp:
    RING_SEGMENTS = 12
    RING_OUTER = 98
    RING_INNER = 62
    RING_CX = 120
    RING_CY = 120

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MedicBot")
        self.root.geometry("900x640")
        self.root.minsize(800, 560)
        try:
            self.root.state("zoomed")
        except Exception:
            pass

        self.checks = []
        self.ring_arcs = []
        self.ring_index = 0
        self.animating = True
        self.anim_delay = 120
        self.anim_job = None
        self.executando = False
        self.proc_manutencao = None

        cfg = carregar_config() or {}
        self.idioma = cfg.get("idioma", "pt")
        if self.idioma not in ("pt", "en", "es"):
            self.idioma = "pt"
        self.cores = CORES_ESCURO
        self.confirmar_ao_cancelar = cfg.get("confirmar_ao_cancelar", True)

        self.root.configure(bg=self.cores["fundo_escuro"])
        self.criar_interface()
        self.iniciar_animacao()
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)

    def criar_interface(self):
        # Carregar logos (guardar em self para não serem apagadas da memória)
        pasta = obter_pasta_script()
        self.logo_header = carregar_logo(pasta, "Logo+nome do lado.png", redimensionar=(9999, 40))
        self.logo_sobre = carregar_logo(pasta, "Logo+Nome abaixo.png", redimensionar=(200,))
        self.logo_icon = carregar_logo(pasta, "Só Logo PNG.png")
        if self.logo_icon:
            try:
                self.root.iconphoto(True, self.logo_icon)
            except Exception:
                pass

        # Container principal: sidebar + conteúdo
        main = tk.Frame(self.root, bg=self.cores["fundo_escuro"])
        main.pack(fill=tk.BOTH, expand=True)

        # ---- Sidebar esquerda (nomes em vez de ícones) ----
        sidebar = tk.Frame(main, width=160, bg=self.cores["fundo_sidebar"])
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        self.sidebar_btns = []

        tk.Frame(sidebar, height=16, bg=self.cores["fundo_sidebar"]).pack()
        for label_key, cmd in [
            ("menu_inicio", self.mostrar_inicio),
            ("menu_o_que_faz", self.mostrar_o_que_faz),
            ("menu_log", self.mostrar_log),
            ("menu_sobre", self.mostrar_sobre),
            ("menu_config", self.mostrar_configuracoes),
        ]:
            btn = tk.Label(
                sidebar, text=self.t(label_key), font=("Segoe UI", 11),
                fg=self.cores["texto"], bg=self.cores["fundo_sidebar"],
                cursor="hand2", anchor="w",
            )
            btn.pack(fill=tk.X, pady=8, padx=12)
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            btn.bind("<Enter>", lambda e, b=btn: b.configure(fg=self.cores["destaque"]))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(fg=self.cores["texto"]))
            self.sidebar_btns.append((btn, label_key))

        # ---- Área de conteúdo ----
        self.content = tk.Frame(main, bg=self.cores["fundo_escuro"])
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Header (logo+nome de lado ou texto)
        header = tk.Frame(self.content, bg=self.cores["fundo_medio"], height=52)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        if self.logo_header:
            tk.Label(
                header, image=self.logo_header,
                bg=self.cores["fundo_medio"],
            ).pack(side=tk.LEFT, padx=24, pady=8)
        else:
            tk.Label(
                header, text="MedicBot", font=("Segoe UI", 18, "bold"),
                fg=self.cores["texto"], bg=self.cores["fundo_medio"],
            ).pack(side=tk.LEFT, padx=24, pady=12)
        badge = tk.Label(
            header, text=" FREE ", font=("Segoe UI", 9, "bold"),
            fg=self.cores["texto"], bg=self.cores["badge"],
        )
        badge.pack(side=tk.LEFT, pady=14)
        tk.Frame(header, bg=self.cores["fundo_medio"]).pack(side=tk.RIGHT, padx=24)

        # Página inicial: coluna esquerda = etapas (uma coluna); direita = status + anel + cards
        self.frame_inicio = tk.Frame(self.content, bg=self.cores["fundo_escuro"])
        self.frame_inicio.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)

        # Container horizontal: esquerda = checkboxes (uma coluna), direita = resto
        linha_principal = tk.Frame(self.frame_inicio, bg=self.cores["fundo_escuro"])
        linha_principal.pack(fill=tk.BOTH, expand=True)

        # ---- Coluna esquerda: apenas uma coluna de etapas ----
        painel_esquerdo = tk.Frame(linha_principal, bg=self.cores["fundo_escuro"], width=320)
        painel_esquerdo.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 24))
        painel_esquerdo.pack_propagate(False)

        self.lbl_selecione_etapas = tk.Label(
            painel_esquerdo,
            text=self.t("selecione_etapas"),
            font=("Segoe UI", 11, "bold"),
            fg=self.cores["texto"],
            bg=self.cores["fundo_escuro"],
            wraplength=300,
            justify=tk.LEFT,
        )
        self.lbl_selecione_etapas.pack(anchor="w", pady=(0, 10))

        frame_cb = tk.Frame(painel_esquerdo, bg=self.cores["fundo_escuro"])
        frame_cb.pack(fill=tk.BOTH, expand=True)
        etapas_salvas = carregar_etapas_salvas()
        cfg_inicial = carregar_config()
        defender_inicial = (cfg_inicial.get("defender_scan", "1") if cfg_inicial else "1")
        self.defender_scan_var = tk.StringVar(value=defender_inicial)
        self.submenu_antivirus_visivel = False

        for i, nome in enumerate(ETAPAS_SHORT, 1):
            valor_inicial = etapas_salvas is not None and i in etapas_salvas
            var = tk.BooleanVar(value=valor_inicial)
            self.checks.append((i, var))

            if i == 5:
                # Container: linha do Antivírus + submenu logo abaixo (como submenu)
                frame_antivirus_container = tk.Frame(frame_cb, bg=self.cores["fundo_escuro"])
                frame_antivirus_container.pack(anchor="w", pady=2)
                frame_row = tk.Frame(frame_antivirus_container, bg=self.cores["fundo_escuro"], cursor="hand2")
                frame_row.pack(anchor="w")
                cb = tk.Checkbutton(
                    frame_row, text="", variable=var,
                    font=("Segoe UI", 10), fg=self.cores["texto"], bg=self.cores["fundo_escuro"],
                    activebackground=self.cores["fundo_escuro"], activeforeground=self.cores["texto"],
                    selectcolor=self.cores["fundo_medio"], highlightthickness=0,
                    cursor="hand2", command=self._ao_mudar_checkbox,
                )
                cb.pack(side=tk.LEFT)
                lbl_antivirus = tk.Label(
                    frame_row, text="Antivírus Windows",
                    font=("Segoe UI", 10), fg=self.cores["texto"], bg=self.cores["fundo_escuro"],
                    cursor="hand2",
                )
                lbl_antivirus.pack(side=tk.LEFT, padx=2)
                # Clicar no nome: marca/desmarca checkbox e mostra/esconde submenu
                lbl_antivirus.bind("<Button-1>", lambda e: self._clicar_label_antivirus())
                self.submenu_antivirus = tk.Frame(frame_antivirus_container, bg=self.cores["fundo_escuro"], padx=20, pady=4)
                for valor, texto in [("1", "Rápida"), ("2", "Completa")]:
                    rb = tk.Radiobutton(
                        self.submenu_antivirus, text=texto, variable=self.defender_scan_var, value=valor,
                        font=("Segoe UI", 9), fg=self.cores["texto_secundario"], bg=self.cores["fundo_escuro"],
                        activebackground=self.cores["fundo_escuro"], activeforeground=self.cores["texto"],
                        selectcolor=self.cores["fundo_medio"], highlightthickness=0,
                        cursor="hand2", command=self._ao_mudar_defender_scan,
                    )
                    rb.pack(anchor="w", pady=1)
                # Mostrar submenu na abertura se etapa já estava salva como selecionada
                if valor_inicial:
                    self.submenu_antivirus.pack(anchor="w", pady=(0, 4))
                    self.submenu_antivirus_visivel = True
            else:
                cb = tk.Checkbutton(
                    frame_cb, text=nome, variable=var,
                    font=("Segoe UI", 10), fg=self.cores["texto"], bg=self.cores["fundo_escuro"],
                    activebackground=self.cores["fundo_escuro"], activeforeground=self.cores["texto"],
                    selectcolor=self.cores["fundo_medio"], highlightthickness=0,
                    cursor="hand2", command=self._ao_mudar_checkbox,
                )
                cb.pack(anchor="w", pady=2)

        self.lbl_info_etapas_demoram = tk.Label(
            painel_esquerdo,
            text=self.t("info_etapas_demoram"),
            font=("Segoe UI", 9),
            fg=self.cores["texto_secundario"],
            bg=self.cores["fundo_escuro"],
            wraplength=300,
            justify=tk.LEFT,
        )
        self.lbl_info_etapas_demoram.pack(anchor="w", pady=(12, 0))

        # ---- Coluna direita: status, anel, cards, texto ----
        painel_direito = tk.Frame(linha_principal, bg=self.cores["fundo_escuro"])
        painel_direito.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.lbl_status = tk.Label(
            painel_direito,
            text=self.t("status_etapas").format(0),
            font=("Segoe UI", 11),
            fg=self.cores["texto"],
            bg=self.cores["fundo_escuro"],
        )
        self.lbl_status.pack(pady=(0, 8))

        centro = tk.Frame(painel_direito, bg=self.cores["fundo_escuro"])
        centro.pack(expand=True)

        self.canvas_ring = tk.Canvas(
            centro, width=240, height=240,
            bg=self.cores["fundo_escuro"], highlightthickness=0,
        )
        self.canvas_ring.pack(pady=12)
        self.desenhar_anel()
        self.canvas_ring.tag_bind("center_btn", "<Button-1>", lambda e: self.ao_clicar_executar())
        self.canvas_ring.tag_bind("center_btn", "<Enter>", lambda e: self.canvas_ring.configure(cursor="hand2"))
        self.canvas_ring.tag_bind("center_btn", "<Leave>", lambda e: self.canvas_ring.configure(cursor=""))

        cards = tk.Frame(centro, bg=self.cores["fundo_escuro"])
        cards.pack(pady=20)

        self.card_limpeza = self.criar_card(cards, "Limpeza", "8", "arquivos e cache")
        self.card_limpeza.pack(side=tk.LEFT, padx=20)
        self.card_sistema = self.criar_card(cards, "Sistema", "6", "antivírus e disco")
        self.card_sistema.pack(side=tk.LEFT, padx=20)

        self.atualizar_cards()

        tk.Label(
            painel_direito,
            text="Clique em EXECUTAR para iniciar. A manutenção roda aqui mesmo, sem abrir outra janela.\nPara tudo funcionar, execute o MedicBot como Administrador (clique direito no atalho > Executar como administrador).",
            font=("Segoe UI", 10),
            fg=self.cores["texto_secundario"],
            bg=self.cores["fundo_escuro"],
            wraplength=380,
            justify=tk.LEFT,
        ).pack(pady=10)

        self.lbl_ajuda = tk.Label(
            painel_direito,
            text=self.t("saiba_etapas"),
            font=("Segoe UI", 10),
            fg=self.cores["destaque"],
            bg=self.cores["fundo_escuro"],
            cursor="hand2",
        )
        self.lbl_ajuda.pack(pady=4)
        self.lbl_ajuda.bind("<Button-1>", lambda e: self.mostrar_o_que_faz())
        self.lbl_ajuda.bind("<Enter>", lambda e: self.lbl_ajuda.configure(fg=self.cores["botao_hover"]))
        self.lbl_ajuda.bind("<Leave>", lambda e: self.lbl_ajuda.configure(fg=self.cores["destaque"]))

        # ---- Painel de execução (barra + minilog + cancelar) - fica abaixo, só aparece ao executar ----
        self.painel_execucao = tk.Frame(painel_direito, bg=self.cores["fundo_escuro"])
        self.lbl_executando = tk.Label(
            self.painel_execucao, text=self.t("executando") + "... 0%",
            font=("Segoe UI", 11, "bold"), fg=self.cores["destaque"], bg=self.cores["fundo_escuro"],
        )
        self.lbl_executando.pack(pady=(12, 4))
        self.progress_bar = ttk.Progressbar(self.painel_execucao, length=320, maximum=100, mode="determinate")
        self.progress_bar.pack(pady=4)
        frame_minilog = tk.Frame(self.painel_execucao, bg=self.cores["fundo_medio"], padx=8, pady=6)
        frame_minilog.pack(fill=tk.BOTH, expand=True, pady=8)
        self.minilog_text = scrolledtext.ScrolledText(
            frame_minilog, height=6, font=("Consolas", 9),
            fg=self.cores["texto"], bg=self.cores["fundo_escuro"], insertbackground=self.cores["texto"],
        )
        self.minilog_text.pack(fill=tk.BOTH, expand=True)
        self.btn_cancelar = tk.Button(
            self.painel_execucao, text=self.t("cancelar"),
            font=("Segoe UI", 10), fg=self.cores["texto"], bg=self.cores["fundo_medio"],
            relief=tk.FLAT, padx=16, pady=6, cursor="hand2", command=self.pedir_confirmar_cancelar,
        )
        self.btn_cancelar.pack(pady=8)
        self.painel_execucao.pack_forget()

        self.atualizar_status_e_cards()

        # ---- Página "O que cada etapa faz" (só explicações, sem checkboxes) ----
        self.frame_o_que_faz = tk.Frame(self.content, bg=self.cores["fundo_escuro"])
        self.frame_o_que_faz.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)
        self.lbl_titulo_o_que_faz = tk.Label(
            self.frame_o_que_faz, text=self.t("titulo_sobre"),
            font=("Segoe UI", 14, "bold"), fg=self.cores["texto"], bg=self.cores["fundo_escuro"],
        )
        self.lbl_titulo_o_que_faz.pack(anchor="w", pady=(0, 16))
        container_desc = tk.Frame(self.frame_o_que_faz, bg=self.cores["fundo_escuro"])
        container_desc.pack(fill=tk.BOTH, expand=True)
        for col in range(4):
            container_desc.columnconfigure(col, weight=1)
        for i, (titulo, desc) in enumerate(ETAPAS_DESCRICOES):
            row, col = i // 4, i % 4
            card = tk.Frame(
                container_desc,
                bg=self.cores["fundo_medio"],
                padx=14,
                pady=14,
                highlightbackground=self.cores["borda_cartao"],
                highlightthickness=1,
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            tk.Label(
                card, text=f"{i + 1}. {titulo}", font=("Segoe UI", 11, "bold"),
                fg=self.cores["texto"], bg=self.cores["fundo_medio"],
            ).pack(anchor="w", pady=(0, 6))
            tk.Label(
                card, text=desc, font=("Segoe UI", 10),
                fg=self.cores["texto_secundario"], bg=self.cores["fundo_medio"],
                wraplength=200, justify=tk.LEFT,
            ).pack(anchor="w")
        self.frame_o_que_faz.pack_forget()

        # ---- Página Log ----
        self.frame_log = tk.Frame(self.content, bg=self.cores["fundo_escuro"])
        self.frame_log.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)
        self.lbl_titulo_log = tk.Label(
            self.frame_log, text=self.t("titulo_log"),
            font=("Segoe UI", 14, "bold"), fg=self.cores["texto"], bg=self.cores["fundo_escuro"],
        )
        self.lbl_titulo_log.pack(anchor="w", pady=(0, 8))
        log_container = tk.Frame(self.frame_log, bg=self.cores["fundo_medio"], padx=8, pady=8)
        log_container.pack(fill=tk.BOTH, expand=True)
        self.log_text = scrolledtext.ScrolledText(
            log_container, height=14, font=("Consolas", 9),
            fg=self.cores["texto"], bg=self.cores["fundo_escuro"], insertbackground=self.cores["texto"],
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.btn_abrir_log = tk.Button(
            self.frame_log, text=self.t("abrir_pasta_log"),
            font=("Segoe UI", 10), fg=self.cores["fundo_escuro"], bg=self.cores["botao"],
            relief=tk.FLAT, padx=16, pady=6, cursor="hand2", command=self.abrir_pasta_log,
        )
        self.btn_abrir_log.pack(pady=12)
        self.frame_log.pack_forget()

        # ---- Página Sobre (conteúdo centralizado) ----
        self.frame_sobre = tk.Frame(self.content, bg=self.cores["fundo_escuro"])
        self.frame_sobre.pack(fill=tk.BOTH, expand=True, padx=32, pady=24)
        # Logo+nome abaixo ou título em texto
        if self.logo_sobre:
            tk.Label(
                self.frame_sobre, image=self.logo_sobre,
                bg=self.cores["fundo_escuro"],
            ).pack(anchor=tk.CENTER, pady=(24, 4))
        else:
            tk.Label(
                self.frame_sobre, text="MedicBot",
                font=("Segoe UI", 26, "bold"), fg=self.cores["texto"], bg=self.cores["fundo_escuro"],
            ).pack(anchor=tk.CENTER, pady=(24, 4))
        self.lbl_sobre_tagline = tk.Label(
            self.frame_sobre, text=self.t("sobre_tagline"),
            font=("Segoe UI", 12), fg=self.cores["destaque"], bg=self.cores["fundo_escuro"],
        )
        self.lbl_sobre_tagline.pack(anchor=tk.CENTER, pady=(0, 20))
        # Texto sobre o programa e desenvolvedor
        self.lbl_sobre_paragrafo = tk.Label(
            self.frame_sobre, text=self.t("sobre_paragrafo"),
            font=("Segoe UI", 11), fg=self.cores["texto_secundario"], bg=self.cores["fundo_escuro"],
            justify=tk.CENTER, wraplength=520,
        )
        self.lbl_sobre_paragrafo.pack(anchor=tk.CENTER, pady=(0, 16))
        # Lista de etapas
        self.lbl_sobre_etapas = tk.Label(
            self.frame_sobre, text=self.t("sobre_etapas"),
            font=("Segoe UI", 10), fg=self.cores["texto_secundario"], bg=self.cores["fundo_escuro"],
            justify=tk.CENTER, wraplength=520,
        )
        self.lbl_sobre_etapas.pack(anchor=tk.CENTER, pady=(0, 28))
        # Instagram do desenvolvedor
        frame_instagram = tk.Frame(self.frame_sobre, bg=self.cores["fundo_escuro"])
        frame_instagram.pack(anchor=tk.CENTER, pady=8)
        self.lbl_sobre_instagram = tk.Label(
            frame_instagram, text=self.t("sobre_instagram"),
            font=("Segoe UI", 11), fg=self.cores["texto"], bg=self.cores["fundo_escuro"],
        )
        self.lbl_sobre_instagram.pack(anchor=tk.CENTER, pady=(0, 8))
        self.btn_sobre_seguir = tk.Button(
            frame_instagram, text=self.t("sobre_botao_seguir"),
            font=("Segoe UI", 11), fg=self.cores["texto"], bg=self.cores["botao"],
            relief=tk.FLAT, padx=20, pady=8, cursor="hand2", command=self.abrir_instagram,
        )
        self.btn_sobre_seguir.pack(anchor=tk.CENTER)
        self.btn_sobre_seguir.bind("<Enter>", lambda e: self.btn_sobre_seguir.configure(bg=self.cores["botao_hover"]))
        self.btn_sobre_seguir.bind("<Leave>", lambda e: self.btn_sobre_seguir.configure(bg=self.cores["botao"]))
        self.frame_sobre.pack_forget()

        # ---- Página Configurações ----
        self.frame_config = tk.Frame(self.content, bg=self.cores["fundo_escuro"])
        self.frame_config.pack(fill=tk.BOTH, expand=True, padx=24, pady=20)
        tk.Label(
            self.frame_config, text=self.t("titulo_config"),
            font=("Segoe UI", 14, "bold"), fg=self.cores["texto"], bg=self.cores["fundo_escuro"],
        ).pack(anchor="w", pady=(0, 16))
        box = tk.Frame(self.frame_config, bg=self.cores["fundo_medio"], padx=24, pady=20, highlightbackground=self.cores["borda_cartao"], highlightthickness=1)
        box.pack(fill=tk.X)
        tk.Label(box, text=self.t("titulo_cancelamento"), font=("Segoe UI", 11, "bold"), fg=self.cores["texto"], bg=self.cores["fundo_medio"]).pack(anchor="w")
        self.var_confirmar_cancelar = tk.BooleanVar(value=self.confirmar_ao_cancelar)
        cb_confirmar = tk.Checkbutton(box, text=self.t("confirmar_ao_cancelar"), variable=self.var_confirmar_cancelar, font=("Segoe UI", 10), fg=self.cores["texto"], bg=self.cores["fundo_medio"], selectcolor=self.cores["fundo_medio"], command=self._ao_trocar_confirmar_cancelar)
        cb_confirmar.pack(anchor="w", pady=4)
        tk.Frame(box, height=12, bg=self.cores["fundo_medio"]).pack()
        tk.Label(box, text=self.t("idioma"), font=("Segoe UI", 11, "bold"), fg=self.cores["texto"], bg=self.cores["fundo_medio"]).pack(anchor="w")
        self.idioma_var = tk.StringVar(value=self.idioma)
        for val, key in [("pt", "idioma_pt"), ("en", "idioma_en"), ("es", "idioma_es")]:
            rb = tk.Radiobutton(box, text=self.t(key), variable=self.idioma_var, value=val, font=("Segoe UI", 10), fg=self.cores["texto"], bg=self.cores["fundo_medio"], selectcolor=self.cores["fundo_medio"], command=self._aplicar_idioma_ao_trocar)
            rb.pack(anchor="w", pady=2)
        self.frame_config.pack_forget()

        self.log("MedicBot iniciado. Selecione as etapas e clique em EXECUTAR.")
        if etapas_salvas is None:
            self.log("Primeira execução: nenhuma etapa selecionada. Marque as que deseja e elas serão lembradas.")

    def criar_card(self, parent, titulo, numero, subtitulo):
        f = tk.Frame(parent, bg=self.cores["fundo_cartao"], padx=24, pady=16, highlightbackground=self.cores["borda_cartao"], highlightthickness=1)
        tk.Label(f, text=numero, font=("Segoe UI", 24, "bold"), fg=self.cores["destaque"], bg=self.cores["fundo_cartao"]).pack()
        tk.Label(f, text=titulo, font=("Segoe UI", 11, "bold"), fg=self.cores["texto_escuro"], bg=self.cores["fundo_cartao"]).pack()
        tk.Label(f, text=subtitulo, font=("Segoe UI", 9), fg=self.cores["texto_escuro"], bg=self.cores["fundo_cartao"]).pack()
        return f

    def _ao_mudar_checkbox(self):
        self.atualizar_status_e_cards()
        salvar_etapas(self.obter_selecionados(), self.defender_scan_var.get())

    def _clicar_label_antivirus(self):
        """Clicar no nome Antivírus: marca/desmarca o checkbox e mostra/esconde o submenu."""
        # Índice 4 em self.checks é a etapa 5 (Antivírus)
        _, var = self.checks[4]
        var.set(not var.get())
        if var.get():
            self.submenu_antivirus.pack(anchor="w", pady=(0, 4))
            self.submenu_antivirus_visivel = True
        else:
            self.submenu_antivirus.pack_forget()
            self.submenu_antivirus_visivel = False
        self._ao_mudar_checkbox()

    def _toggle_submenu_antivirus(self):
        """Abre ou fecha o submenu Rápida/Completa ao clicar em Antivírus Windows."""
        if self.submenu_antivirus_visivel:
            self.submenu_antivirus.pack_forget()
            self.submenu_antivirus_visivel = False
        else:
            self.submenu_antivirus.pack(anchor="w", pady=(0, 4))
            self.submenu_antivirus_visivel = True

    def _ao_mudar_defender_scan(self):
        salvar_etapas(self.obter_selecionados(), self.defender_scan_var.get())

    def _ao_trocar_confirmar_cancelar(self):
        self.confirmar_ao_cancelar = self.var_confirmar_cancelar.get()
        salvar_config_geral(confirmar_cancelar=self.confirmar_ao_cancelar)

    def _aplicar_idioma_ao_trocar(self):
        self.idioma = self.idioma_var.get()
        salvar_config_geral(idioma=self.idioma)
        self._atualizar_ui_idioma()

    def _atualizar_ui_idioma(self):
        """Atualiza textos da interface para o idioma atual."""
        for btn, key in self.sidebar_btns:
            btn.configure(text=self.t(key))
        self.lbl_selecione_etapas.configure(text=self.t("selecione_etapas"))
        self.lbl_status.configure(text=self.t("status_etapas").format(len(self.obter_selecionados())))
        self.lbl_ajuda.configure(text=self.t("saiba_etapas"))
        self.btn_cancelar.configure(text=self.t("cancelar"))
        self.lbl_titulo_o_que_faz.configure(text=self.t("titulo_sobre"))
        self.lbl_titulo_log.configure(text=self.t("titulo_log"))
        self.btn_abrir_log.configure(text=self.t("abrir_pasta_log"))
        self.lbl_sobre_tagline.configure(text=self.t("sobre_tagline"))
        self.lbl_sobre_paragrafo.configure(text=self.t("sobre_paragrafo"))
        self.lbl_sobre_etapas.configure(text=self.t("sobre_etapas"))
        self.lbl_sobre_instagram.configure(text=self.t("sobre_instagram"))
        self.btn_sobre_seguir.configure(text=self.t("sobre_botao_seguir"))
        self.lbl_info_etapas_demoram.configure(text=self.t("info_etapas_demoram"))
        self.desenhar_anel()

    def t(self, key):
        """Texto traduzido para o idioma atual."""
        return STRINGS.get(self.idioma, STRINGS["pt"]).get(key, STRINGS["pt"].get(key, key))

    def atualizar_cards(self):
        sel = set(self.obter_selecionados())
        n_limpeza = len(sel & ETAPAS_LIMPEZA)
        n_sistema = len(sel & ETAPAS_SISTEMA)
        for card, n in [(self.card_limpeza, n_limpeza), (self.card_sistema, n_sistema)]:
            card.winfo_children()[0].configure(text=str(n))

    def desenhar_anel(self):
        self.canvas_ring.delete("all")
        cx, cy = self.RING_CX, self.RING_CY
        ro, ri = self.RING_OUTER, self.RING_INNER
        self.ring_arcs.clear()
        for i in range(self.RING_SEGMENTS):
            start = 90 - i * (360 / self.RING_SEGMENTS)
            extent = 360 / self.RING_SEGMENTS - 2
            color = self.cores["anel_brilho"] if i == self.ring_index else self.cores["anel_dim"]
            # Arco em coordenadas tk (start em graus, extent)
            id_ = self.canvas_ring.create_arc(
                cx - ro, cy - ro, cx + ro, cy + ro,
                start=start, extent=extent, style=tk.ARC, outline=color, width=12,
            )
            self.ring_arcs.append(id_)
        # Círculo interno (fundo do botão) – todo clicável; fundo claro para quebrar o verde
        self.canvas_ring.create_oval(cx - ri, cy - ri, cx + ri, cy + ri, fill=self.cores["botao_centro"], outline=self.cores["borda_cartao"], width=2, tags="center_btn")
        texto_btn = self.t("executando") if getattr(self, "executando", False) else self.t("executar")
        self.canvas_ring.create_text(cx, cy, text=texto_btn, font=("Segoe UI", 14, "bold"), fill=self.cores["texto_escuro"], tags="center_btn")

    def animar_anel(self):
        if not self.animating:
            return
        self.ring_index = (self.ring_index + 1) % self.RING_SEGMENTS
        self.desenhar_anel()
        self.anim_job = self.root.after(self.anim_delay, self.animar_anel)

    def iniciar_animacao(self):
        self.animating = True
        self.anim_delay = 120
        self.animar_anel()

    def _append_minilog(self, line):
        self.minilog_text.insert(tk.END, line + "\n")
        self.minilog_text.see(tk.END)
        # Detectar início de etapa: "ETAPA X/Y - Nome" (Y = total selecionado)
        m_etapa = re.search(r"ETAPA\s*(\d+)/(\d+)\s*-\s*(.+)", line)
        if m_etapa:
            n = int(m_etapa.group(1))
            total = int(m_etapa.group(2))
            nome = m_etapa.group(3).strip()
            pct = min(99, round((n - 1) / total * 100))  # Ainda não concluiu
            self.progress_bar["value"] = pct
            self.lbl_executando.configure(text=f"Etapa {n} de {total}: {nome} ({pct}%)")
            return
        # Detectar conclusão de etapa: ">>> ETAPA X/Y CONCLUÍDA"
        m_concluida = re.search(r">>>\s*ETAPA\s*(\d+)/(\d+)\s*CONCLUÍDA", line)
        if m_concluida:
            n = int(m_concluida.group(1))
            total = int(m_concluida.group(2))
            pct = min(100, round(n / total * 100))
            self.progress_bar["value"] = pct
            self.lbl_executando.configure(text=f"Etapa {n} de {total} concluída ({pct}%)")
            return
        # Detectar timeout ou aviso para atualizar status
        if "timeout" in line.lower():
            self.lbl_executando.configure(text=self.lbl_executando.cget("text").replace("...", " (timeout)"))
        # Detectar "MANUTENÇÃO CONCLUÍDA"
        if "MANUTENÇÃO CONCLUÍDA" in line:
            self.progress_bar["value"] = 100
            self.lbl_executando.configure(text="Concluído! 100%")

    def pedir_confirmar_cancelar(self):
        """Se config pedir confirmação, mostra janela 'Certeza? Sim/Não' e opção 'Não mostrar novamente'. Senão cancela direto."""
        if not self.confirmar_ao_cancelar:
            self.cancelar_manutencao()
            return
        d = tk.Toplevel(self.root)
        d.title(self.t("confirmar_cancelar_titulo"))
        d.resizable(False, False)
        d.configure(bg=self.cores["fundo_medio"])
        d.transient(self.root)
        d.grab_set()
        frame = tk.Frame(d, bg=self.cores["fundo_medio"], padx=24, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(frame, text=self.t("confirmar_cancelar_msg"), font=("Segoe UI", 12, "bold"), fg=self.cores["texto"], bg=self.cores["fundo_medio"]).pack(anchor="w")
        tk.Label(frame, text=self.t("confirmar_cancelar_dica"), font=("Segoe UI", 10), fg=self.cores["texto_secundario"], bg=self.cores["fundo_medio"], wraplength=360, justify=tk.LEFT).pack(anchor="w", pady=(8, 12))
        var_nao_mostrar = tk.BooleanVar(value=False)
        cb = tk.Checkbutton(frame, text=self.t("nao_mostrar_novamente"), variable=var_nao_mostrar, font=("Segoe UI", 10), fg=self.cores["texto"], bg=self.cores["fundo_medio"], selectcolor=self.cores["fundo_escuro"], activebackground=self.cores["fundo_medio"], activeforeground=self.cores["texto"])
        cb.pack(anchor="w", pady=(0, 16))
        bts = tk.Frame(frame, bg=self.cores["fundo_medio"])
        bts.pack(anchor="e")
        def on_nao():
            d.destroy()
        def on_sim():
            if var_nao_mostrar.get():
                self.confirmar_ao_cancelar = False
                salvar_config_geral(confirmar_cancelar=False)
            d.destroy()
            self.cancelar_manutencao()
        tk.Button(bts, text=self.t("nao"), font=("Segoe UI", 10), fg=self.cores["texto"], bg=self.cores["fundo_escuro"], relief=tk.FLAT, padx=16, pady=6, cursor="hand2", command=on_nao).pack(side=tk.RIGHT, padx=4)
        tk.Button(bts, text=self.t("sim"), font=("Segoe UI", 10), fg=self.cores["texto"], bg=self.cores["botao"], relief=tk.FLAT, padx=16, pady=6, cursor="hand2", command=on_sim).pack(side=tk.RIGHT)
        d.geometry("420x220")
        d.update_idletasks()
        w, h = d.winfo_reqwidth(), d.winfo_reqheight()
        x = max(0, (d.winfo_screenwidth() - w) // 2)
        y = max(0, (d.winfo_screenheight() - h) // 2)
        d.geometry(f"+{x}+{y}")
        d.wait_window()

    def cancelar_manutencao(self):
        if self.proc_manutencao and self.proc_manutencao.poll() is None:
            self._cancelamento_pelo_usuario = True
            try:
                _matar_arvore_processo(self.proc_manutencao)
            except Exception:
                try:
                    self.proc_manutencao.terminate()
                except Exception:
                    pass
            self.root.after(100, lambda: self._manutencao_terminou(-999))

    def ao_clicar_executar(self):
        if self.executando:
            return
        sel = self.obter_selecionados()
        if not sel:
            messagebox.showwarning("MedicBot", "Marque pelo menos uma etapa abaixo.")
            return
        self.executando = True
        self._manutencao_ja_terminou = False
        self.anim_delay = 55
        self.proc_manutencao = None

        self.minilog_text.delete("1.0", tk.END)
        self.progress_bar["value"] = 0
        self.lbl_executando.configure(text=self.t("executando") + "... 0%")
        self.painel_execucao.pack(fill=tk.X, pady=(8, 0))
        self.desenhar_anel()

        def on_line(line):
            self.root.after(0, lambda l=line: self._append_minilog(l))
            self.root.after(0, lambda l=line: self.log(l))

        def on_done(returncode):
            self.root.after(0, lambda: self._manutencao_terminou(returncode))

        self.log("Iniciando manutenção...")
        steps = sel if len(sel) < 14 else None
        defender_scan = self.defender_scan_var.get()
        if defender_scan not in ("1", "2"):
            defender_scan = "1"
        ok, err, proc = executar_manutencao(steps=steps, on_line=on_line, on_done=on_done, defender_scan_type=defender_scan)
        if ok:
            self.proc_manutencao = proc
        else:
            self.executando = False
            self.anim_delay = 120
            self.painel_execucao.pack_forget()
            self.log(f"Erro: {err}")
            messagebox.showerror("MedicBot", f"Não foi possível iniciar:\n{err}")

    def _manutencao_terminou(self, returncode):
        if getattr(self, "_manutencao_ja_terminou", False):
            return
        if getattr(self, "_cancelamento_pelo_usuario", False):
            self._cancelamento_pelo_usuario = False
            returncode = -999
        self._manutencao_ja_terminou = True
        self.executando = False
        self.anim_delay = 120
        self.proc_manutencao = None
        self.painel_execucao.pack_forget()
        self.desenhar_anel()
        if returncode == -999:
            self.log("--- Manutenção cancelada pelo usuário. ---")
        elif returncode == 0:
            self.log("--- Manutenção concluída. ---")
            messagebox.showinfo("MedicBot", "Manutenção concluída.")
        else:
            self.log("--- Manutenção finalizada com erros (pode ser falta de permissão de administrador). ---")
            messagebox.showwarning(
                "MedicBot",
                "A manutenção terminou com erros.\n\nExecute o MedicBot como Administrador (clique direito no atalho > Executar como administrador) e tente novamente.",
            )

    def mostrar_pagina(self, frame):
        self.frame_inicio.pack_forget()
        self.frame_o_que_faz.pack_forget()
        self.frame_log.pack_forget()
        self.frame_sobre.pack_forget()
        self.frame_config.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True, padx=24 if frame == self.frame_inicio else 32, pady=20 if frame == self.frame_inicio else 24)

    def mostrar_inicio(self):
        self.mostrar_pagina(self.frame_inicio)

    def mostrar_o_que_faz(self):
        self.mostrar_pagina(self.frame_o_que_faz)

    def mostrar_log(self):
        self.mostrar_pagina(self.frame_log)

    def mostrar_sobre(self):
        self.mostrar_pagina(self.frame_sobre)

    def mostrar_configuracoes(self):
        self.var_confirmar_cancelar.set(self.confirmar_ao_cancelar)
        self.mostrar_pagina(self.frame_config)

    def atualizar_status_e_cards(self):
        n = len(self.obter_selecionados())
        self.lbl_status.configure(text=self.t("status_etapas").format(n))
        self.atualizar_cards()

    def obter_selecionados(self):
        return [i for i, var in self.checks if var.get()]

    def ao_fechar(self):
        salvar_etapas(self.obter_selecionados(), self.defender_scan_var.get())
        if self.proc_manutencao and self.proc_manutencao.poll() is None:
            try:
                _matar_arvore_processo(self.proc_manutencao)
            except Exception:
                pass
        self.root.destroy()

    def executar_selecionados(self):
        sel = self.obter_selecionados()
        if not sel:
            messagebox.showwarning("MedicBot", "Marque pelo menos uma etapa.")
            return
        ok, err, _ = executar_manutencao(steps=sel)
        if ok:
            self.log("Manutenção iniciada (Administrador).")
            messagebox.showinfo("MedicBot", "A manutenção está rodando em outra janela.")
        else:
            self.log(f"Erro: {err}")
            messagebox.showerror("MedicBot", str(err))

    def abrir_pasta_log(self):
        pasta = obter_pasta_script()
        log_file = os.path.join(pasta, "MedicBot_log.txt")
        if os.path.isfile(log_file):
            os.startfile(log_file)
        else:
            os.startfile(pasta)
        self.log("Pasta do log aberta.")

    def abrir_instagram(self):
        try:
            webbrowser.open(INSTAGRAM_MEDICBOT)
        except Exception:
            pass

    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MedicBotApp()
    app.run()
