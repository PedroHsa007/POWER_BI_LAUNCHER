import sys
import os
import json
import html
import unicodedata
import webbrowser
import shutil
import uuid
from functools import partial
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QScrollArea, QGraphicsDropShadowEffect, QTextEdit,
    QMessageBox, QFrame, QLineEdit, QToolButton, QFileDialog
)
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QColor, QPixmap, QDesktopServices, QFontMetrics
from PySide6.QtCore import QUrl

APP_NAME = "Power BI Launcher"

# Pasta onde ficam os ficheiros json (dashboards e feedback).
# Por defeito é a pasta "dados" ao lado deste ficheiro. Se quiseres que
# vários utilizadores partilhem o mesmo feedback, aponta para uma pasta
# na rede com a variável de ambiente LAUNCHER_DADOS.
PASTA_DADOS = os.environ.get("LAUNCHER_DADOS") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "dados")
FICHEIRO_DASHBOARDS = os.path.join(PASTA_DADOS, "dashboards.json")
FICHEIRO_DASHBOARDS_EXEMPLO = os.path.join(PASTA_DADOS, "dashboards.exemplo.json")
FICHEIRO_FEEDBACK = os.path.join(PASTA_DADOS, "feedback.json")
FICHEIRO_LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "Public", "Logo - Ge.png")

# Formato de cada dashboard: nome, setor, link, icone, pre_visualizacao e
# data_atualizacao. Os campos setor, pre_visualizacao e data_atualizacao são opcionais.
# url, emoji e data continuam aceitos para compatibilidade com JSONs antigos.

STYLE = """
QWidget { color: #e8f0f1; }
QDialog, QMessageBox { background-color: #172528; color: #e8f0f1; }
QMessageBox QLabel { color: #e8f0f1; }
QMessageBox QPushButton { background-color: #c2ce45; color: #172528; border: none;
                          border-radius: 5px; padding: 6px 16px; min-width: 64px; font-weight: bold; }
QMessageBox QPushButton:hover { background-color: #d0dc56; }
QWidget#MainWindow { background-color: #10191b; }
QScrollArea { border: none; background-color: transparent; }
QWidget#ScrollContent { background-color: transparent; }
QLabel#Title { font-size: 20px; font-weight: 800; color: #c2ce45; }
QLabel#HistoryTitle { font-size: 12px; font-weight: 700; color: #c2ce45; padding: 4px 2px; }
QPushButton#AppCard { background-color: #1a292c; border: 1px solid #294044; border-radius: 12px; }
QPushButton#AppCard:hover { border: 2px solid #c2ce45; background-color: #203438; }
QLabel#CardText { font-size: 13px; font-weight: 700; color: #e8f0f1; }
QLabel#CardIcon { font-size: 36px; }
QLabel#CardSector { font-size: 10px; color: #c2ce45; }
QLabel#CardPreview { background-color: #10191b; border-radius: 5px; }
QLabel#CardDate { font-size: 10px; color: #b8c6c8; }
QLineEdit#DashboardFilter { background-color: #172528; color: #e8f0f1; border: 1px solid #345257;
                             border-radius: 8px; padding: 8px 10px; font-size: 12px; }
QLineEdit#DashboardFilter:focus { border-color: #c2ce45; }
QLabel#DashboardCount { color: #b8c6c8; font-size: 11px; }
QWidget#StatusBar { background-color: #055f6b; min-height: 10px; max-height: 10px; }
QFrame#ChatBox { background-color: #172528; border-radius: 15px; border: 1px solid #294044; }
QWidget#ChatHeader { background-color: #055f6b; border-top-left-radius: 14px; border-top-right-radius: 14px; }
QLabel#ChatHeaderText { color: #ffffff; font-size: 14px; font-weight: bold; }
QPushButton#BackBtn { background-color: #c2ce45; color: #172528; font-size: 10px; font-weight: bold;
                      border-radius: 4px; padding: 2px 6px; border: none; }
QLabel#BotBubble { background-color: #223438; border-radius: 10px; padding: 10px; color: #e8f0f1; font-size: 12px; }
QPushButton#ChatOption { background-color: #1a292c; border: 1px solid #345257; border-radius: 8px;
                         padding: 10px; text-align: left; font-size: 12px; color: #e8f0f1; }
QPushButton#ChatOption:hover { background-color: #203438; border-color: #c2ce45; }
QPushButton#SendFeedback { background-color: #c2ce45; color: #172528; border-radius: 6px; font-weight: bold; font-size: 11px; }
QPushButton#SendFeedback:hover { background-color: #d0dc56; }
QPushButton#AttachFeedback { background-color: #223438; color: #e8f0f1; border: 1px solid #345257;
                             border-radius: 6px; padding: 5px; font-size: 11px; }
QPushButton#AttachFeedback:hover { border-color: #c2ce45; }
QPushButton#RemoveAttachment { background-color: #223438; color: #e8f0f1;
                               border: 1px solid #345257; border-radius: 5px; }
QPushButton#RemoveAttachment:hover { border-color: #c2ce45; }
QLabel#AttachmentName { color: #b8c6c8; font-size: 10px; }
QPushButton#OpenAttachment { background-color: #055f6b; color: #ffffff; border: none;
                             border-radius: 5px; padding: 4px 8px; }
QPushButton#OpenAttachment:hover { background-color: #087583; }
QLineEdit, QTextEdit { background-color: #10191b; color: #e8f0f1; border: 1px solid #345257;
                       border-radius: 8px; padding: 5px; font-size: 11px; }
QLineEdit { padding: 2px 6px; }
QLabel#EmptyNotice { color: #b8c6c8; font-size: 13px; }
QWidget#FeedbackPanel { background-color: #141f21; }
QFrame#FeedbackItem { background: #1a292c; border: 1px solid #294044; border-radius: 6px; }
QToolButton#FeedbackToggle { background: transparent; color: #e8f0f1; border: none;
                             text-align: left; padding: 7px; font-size: 11px; }
QToolButton#FeedbackToggle:hover { color: #c2ce45; }
QLabel#FeedbackDetails { color: #d0dcde; font-size: 11px; padding: 2px 7px 8px; }
QPushButton#DeleteFeedback { background-color: #223438; border: 1px solid #345257; border-radius: 5px; }
QPushButton#DeleteFeedback:hover { border-color: #c2ce45; }
QScrollBar:vertical { background: #141f21; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background: #345257; min-height: 20px; border-radius: 5px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
"""


def ler_json(caminho, se_falhar):
    # se o ficheiro não existe ou está estragado, devolve o valor por defeito
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return se_falhar


def gravar_json(caminho, dados):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)


class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setWindowTitle(APP_NAME)
        self.resize(1000, 520)
        self.opcao = ""   # "Melhoria" ou "Relatar Erro"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        conteudo = QWidget()
        main = QVBoxLayout(conteudo)
        main.setContentsMargins(30, 25, 30, 25)
        main.setSpacing(20)

        cabecalho = QWidget()
        cabecalho_layout = QHBoxLayout(cabecalho)
        cabecalho_layout.setContentsMargins(0, 0, 0, 0)
        cabecalho_layout.setSpacing(14)

        logo = QLabel()
        logo.setObjectName("Logo")
        logo.setAccessibleName("Logo Gestão Estratégica")
        pixmap = QPixmap(FICHEIRO_LOGO)
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(
                150, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setFixedSize(150, 90)
        cabecalho_layout.addWidget(logo)

        titulo = QLabel(APP_NAME)
        titulo.setObjectName("Title")
        cabecalho_layout.addWidget(titulo)
        cabecalho_layout.addStretch()
        main.addWidget(cabecalho)

        # cards dos dashboards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        area = QWidget()
        area.setObjectName("ScrollContent")
        self.scroll.setWidget(area)
        self.grid = QGridLayout(area)
        self.grid.setSpacing(20)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.atualizador_grade = QTimer(self)
        self.atualizador_grade.setSingleShot(True)
        self.atualizador_grade.timeout.connect(self.filtrar_dashboards)

        ficheiro_dashboards = (FICHEIRO_DASHBOARDS
                               if os.path.isfile(FICHEIRO_DASHBOARDS)
                               else FICHEIRO_DASHBOARDS_EXEMPLO)
        dashboards = ler_json(ficheiro_dashboards, [])
        if not isinstance(dashboards, list):
            dashboards = []
        # ignora entradas sem nome ou sem url
        dashboards = [
            d for d in dashboards
            if isinstance(d, dict) and d.get("nome") and (d.get("link") or d.get("url"))
        ]

        self.dashboards = dashboards
        filtro_linha = QWidget()
        filtro_layout = QHBoxLayout(filtro_linha)
        filtro_layout.setContentsMargins(0, 0, 0, 0)
        self.filtro_nome = QLineEdit()
        self.filtro_nome.setObjectName("DashboardFilter")
        self.filtro_nome.setPlaceholderText("Buscar BI pelo nome...")
        self.filtro_nome.setClearButtonEnabled(True)
        self.filtro_nome.textChanged.connect(self.filtrar_dashboards)
        filtro_layout.addWidget(self.filtro_nome, 1)
        self.contagem_dashboards = QLabel()
        self.contagem_dashboards.setObjectName("DashboardCount")
        filtro_layout.addWidget(self.contagem_dashboards)
        main.addWidget(filtro_linha)
        self.filtrar_dashboards()

        # painel da direita com o feedback já enviado
        self.painel = QScrollArea()
        self.painel.setFixedWidth(220)
        self.painel.setWidgetResizable(True)
        self.painel.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.painel.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        lista = QWidget()
        lista.setObjectName("FeedbackPanel")
        self.lista_layout = QVBoxLayout(lista)
        self.lista_layout.setAlignment(Qt.AlignTop)
        t = QLabel("Feedback enviado")
        t.setObjectName("HistoryTitle")
        self.lista_layout.addWidget(t)
        self.painel.setWidget(lista)

        linha = QWidget()
        ll = QHBoxLayout(linha)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(10)
        ll.addWidget(self.scroll, 1)
        ll.addWidget(self.painel)
        main.addWidget(linha)

        outer.addWidget(conteudo)
        barra = QWidget()
        barra.setObjectName("StatusBar")
        outer.addWidget(barra)

        self.montar_chat()

        # feedback que já estava guardado
        for item in ler_json(FICHEIRO_FEEDBACK, []):
            self.mostrar_feedback(item)

    # ---------- cards ----------
    @staticmethod
    def normalizar_texto(texto):
        normalizado = unicodedata.normalize("NFKD", texto.casefold())
        return "".join(caractere for caractere in normalizado
                       if not unicodedata.combining(caractere))

    def filtrar_dashboards(self):
        termo = self.normalizar_texto(self.filtro_nome.text().strip())
        encontrados = [
            dashboard for dashboard in self.dashboards
            if termo in self.normalizar_texto(str(dashboard["nome"]))
        ]

        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.deleteLater()

        if not self.dashboards:
            aviso = QLabel("Nenhum dashboard configurado.\n"
                           "Adiciona-os em dados/dashboards.json")
            aviso.setObjectName("EmptyNotice")
            self.grid.addWidget(aviso, 0, 0)
        elif not encontrados:
            aviso = QLabel("Nenhum BI encontrado com esse nome.")
            aviso.setObjectName("EmptyNotice")
            self.grid.addWidget(aviso, 0, 0)
        else:
            largura_card = 180
            espacamento = self.grid.horizontalSpacing()
            colunas = max(
                1,
                (self.scroll.viewport().width() + espacamento)
                // (largura_card + espacamento),
            )
            encontrados.sort(
                key=lambda dashboard: self.normalizar_texto(
                    str(dashboard["nome"]))
            )
            for indice, dashboard in enumerate(encontrados):
                self.grid.addWidget(
                    self.criar_card(dashboard),
                    indice // colunas,
                    indice % colunas,
                )

        self.contagem_dashboards.setText(
            f"{len(encontrados)} de {len(self.dashboards)} BI(s)")

    def criar_card(self, d):
        link = d.get("link") or d.get("url")
        btn = QPushButton()
        btn.setObjectName("AppCard")
        btn.setFixedWidth(180)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setAccessibleName(f"{d['nome']}, abrir dashboard")
        btn.clicked.connect(partial(webbrowser.open, link))
        lay = QVBoxLayout(btn)
        lay.setContentsMargins(5, 5, 5, 5)
        lay.setSpacing(2)

        miniatura = QLabel()
        miniatura.setAlignment(Qt.AlignCenter)
        miniatura.setFixedHeight(64)
        caminho_preview = d.get("pre_visualizacao")
        imagem = QPixmap()
        if caminho_preview:
            caminho_preview = os.path.expanduser(str(caminho_preview))
            if not os.path.isabs(caminho_preview):
                caminho_preview = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)), caminho_preview)
            imagem.load(caminho_preview)

        if not imagem.isNull():
            miniatura.setObjectName("CardPreview")
            miniatura.setPixmap(imagem.scaled(
                160, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            miniatura.setAccessibleName(f"Pré-visualização de {d['nome']}")
        else:
            miniatura.setObjectName("CardIcon")
            miniatura.setText(d.get("icone") or d.get("emoji") or "📊")
            miniatura.setStyleSheet("font-size:36px;")
        miniatura.setAttribute(Qt.WA_TransparentForMouseEvents)

        nome = QLabel(d["nome"])
        nome.setObjectName("CardText")
        nome.setAlignment(Qt.AlignCenter)
        nome.setWordWrap(True)
        nome.setToolTip(d["nome"])
        largura_texto = 168
        altura_nome = QFontMetrics(nome.font()).boundingRect(
            QRect(0, 0, largura_texto, 1000),
            Qt.AlignCenter | Qt.TextWordWrap,
            nome.text(),
        ).height()
        nome.setMinimumHeight(altura_nome)

        setor_texto = str(d.get("setor", "")).strip()
        setor = QLabel(setor_texto)
        setor.setObjectName("CardSector")
        setor.setAlignment(Qt.AlignCenter)
        setor.setWordWrap(True)
        setor.setVisible(bool(setor_texto))
        altura_setor = 0
        if setor_texto:
            altura_setor = QFontMetrics(setor.font()).boundingRect(
                QRect(0, 0, largura_texto, 1000),
                Qt.AlignCenter | Qt.TextWordWrap,
                setor_texto,
            ).height()
            setor.setMinimumHeight(altura_setor)

        data = QLabel()
        data.setObjectName("CardDate")
        try:
            valor_data = d.get("data_atualizacao") or d["data"]
            data_atualizacao = datetime.fromisoformat(str(valor_data)).strftime("%d/%m/%Y")
            data.setText(f"Atualizado em: {data_atualizacao}")
        except (KeyError, TypeError, ValueError):
            data.setText("Atualização não informada")
        data.setAlignment(Qt.AlignCenter)
        altura_data = QFontMetrics(data.font()).boundingRect(
            QRect(0, 0, largura_texto, 1000),
            Qt.AlignCenter | Qt.TextWordWrap,
            data.text(),
        ).height()
        data.setWordWrap(True)
        data.setMinimumHeight(altura_data)
        btn.setFixedHeight(max(175, 64 + altura_nome + altura_setor + altura_data + 22))

        for widget in (miniatura, nome, setor, data):
            widget.setAttribute(Qt.WA_TransparentForMouseEvents)
            lay.addWidget(widget)
        return btn

    # ---------- chat ----------
    def montar_chat(self):
        self.chat_btn = QPushButton("🤖", self)
        self.chat_btn.setFixedSize(50, 50)
        self.chat_btn.setCursor(Qt.PointingHandCursor)
        self.chat_btn.setStyleSheet(
            "QPushButton{border-radius:25px;background-color:#055f6b;color:white;font-size:20px;border:none;}"
            "QPushButton:hover{background-color:#087583;}")
        self.chat_btn.clicked.connect(self.abrir_fechar_chat)

        self.chat_box = QFrame(self)
        self.chat_box.setObjectName("ChatBox")
        self.chat_box.setFixedSize(290, 300)
        self.chat_box.hide()
        v = QVBoxLayout(self.chat_box)
        v.setContentsMargins(0, 0, 0, 10)
        v.setSpacing(0)

        cabecalho = QWidget()
        cabecalho.setObjectName("ChatHeader")
        cabecalho.setFixedHeight(50)
        h = QHBoxLayout(cabecalho)
        h.setContentsMargins(10, 0, 10, 0)
        self.btn_voltar = QPushButton("VOLTAR")
        self.btn_voltar.setObjectName("BackBtn")
        self.btn_voltar.clicked.connect(self.menu_inicial)
        self.btn_voltar.hide()
        nome_chat = QLabel("Assistente")
        nome_chat.setObjectName("ChatHeaderText")
        h.addWidget(self.btn_voltar)
        h.addStretch()
        h.addWidget(nome_chat)
        h.addStretch()
        v.addWidget(cabecalho)

        corpo = QWidget()
        self.corpo = QVBoxLayout(corpo)
        self.corpo.setContentsMargins(15, 15, 15, 10)
        self.corpo.setSpacing(8)

        self.msg = QLabel("Olá 👋 Como posso ajudar?")
        self.msg.setObjectName("BotBubble")
        self.msg.setWordWrap(True)
        self.corpo.addWidget(self.msg)

        self.btn_melhoria = QPushButton("📝 Sugestão de Melhoria")
        self.btn_melhoria.setObjectName("ChatOption")
        self.btn_melhoria.clicked.connect(lambda: self.escolher("Melhoria"))
        self.btn_erro = QPushButton("⚠️ Relatar Erro")
        self.btn_erro.setObjectName("ChatOption")
        self.btn_erro.clicked.connect(lambda: self.escolher("Relatar Erro"))
        self.corpo.addWidget(self.btn_melhoria)
        self.corpo.addWidget(self.btn_erro)

        self.campo_email = QLineEdit()
        self.campo_email.setPlaceholderText("Seu email")
        self.campo_email.setFixedHeight(28)
        self.campo_texto = QTextEdit()
        self.campo_texto.setPlaceholderText("Escreva os detalhes aqui...")
        self.campo_texto.setFixedHeight(60)
        self.anexo_selecionado = ""
        self.linha_anexo = QWidget()
        layout_anexo = QHBoxLayout(self.linha_anexo)
        layout_anexo.setContentsMargins(0, 0, 0, 0)
        layout_anexo.setSpacing(6)
        self.btn_anexar = QPushButton("📎 Anexar foto/documento")
        self.btn_anexar.setObjectName("AttachFeedback")
        self.btn_anexar.clicked.connect(self.selecionar_anexo)
        self.nome_anexo = QLabel()
        self.nome_anexo.setObjectName("AttachmentName")
        self.nome_anexo.setWordWrap(True)
        self.btn_remover_anexo = QPushButton("×")
        self.btn_remover_anexo.setObjectName("RemoveAttachment")
        self.btn_remover_anexo.setFixedSize(24, 24)
        self.btn_remover_anexo.setToolTip("Remover anexo selecionado")
        self.btn_remover_anexo.clicked.connect(self.remover_anexo)
        self.btn_remover_anexo.hide()
        layout_anexo.addWidget(self.btn_anexar)
        layout_anexo.addWidget(self.nome_anexo, 1)
        layout_anexo.addWidget(self.btn_remover_anexo)
        self.btn_enviar = QPushButton("Enviar Mensagem")
        self.btn_enviar.setObjectName("SendFeedback")
        self.btn_enviar.setFixedHeight(30)
        self.btn_enviar.clicked.connect(self.enviar_feedback)
        for w in (self.campo_email, self.campo_texto, self.linha_anexo,
                  self.btn_enviar):
            w.hide()
            self.corpo.addWidget(w)
        self.corpo.addStretch()
        v.addWidget(corpo)

        sombra = QGraphicsDropShadowEffect()
        sombra.setBlurRadius(15)
        sombra.setColor(QColor(0, 0, 0, 50))
        sombra.setYOffset(4)
        self.chat_box.setGraphicsEffect(sombra)
        self.posicionar_chat()

    def abrir_fechar_chat(self):
        if self.chat_box.isVisible():
            self.chat_box.hide()
        else:
            self.menu_inicial()
            self.chat_box.show()

    def menu_inicial(self):
        self.btn_voltar.hide()
        for w in (self.campo_email, self.campo_texto, self.linha_anexo,
                  self.btn_enviar):
            w.hide()
        self.campo_email.clear()
        self.campo_texto.clear()
        self.anexo_selecionado = ""
        self.nome_anexo.clear()
        self.btn_remover_anexo.hide()
        self.btn_melhoria.show()
        self.btn_erro.show()
        self.msg.setText("Olá 👋 Como posso ajudar?")
        self.chat_box.setFixedHeight(280)
        self.posicionar_chat()

    def escolher(self, opcao):
        self.opcao = opcao
        self.btn_voltar.show()
        self.btn_melhoria.hide()
        self.btn_erro.hide()
        self.msg.setText(f"Selecionou: {opcao}\nDescreva abaixo:")
        for w in (self.campo_email, self.campo_texto, self.linha_anexo,
                  self.btn_enviar):
            w.show()
        self.chat_box.setFixedHeight(400)
        self.posicionar_chat()

    def selecionar_anexo(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Anexar foto ou documento",
            "",
            "Fotos e documentos (*.png *.jpg *.jpeg *.gif *.bmp *.webp "
            "*.pdf *.doc *.docx *.xls *.xlsx *.ppt *.pptx *.txt *.csv)",
        )
        if caminho:
            self.anexo_selecionado = caminho
            self.nome_anexo.setText(os.path.basename(caminho))
            self.nome_anexo.setToolTip(caminho)
            self.btn_remover_anexo.show()

    def remover_anexo(self):
        self.anexo_selecionado = ""
        self.nome_anexo.clear()
        self.nome_anexo.setToolTip("")
        self.btn_remover_anexo.hide()

    def enviar_feedback(self):
        texto = self.campo_texto.toPlainText().strip()
        email = self.campo_email.text().strip()
        if not texto:
            QMessageBox.warning(self, "Aviso", "Escreva uma mensagem antes de enviar.")
            return
        if "@" not in email:
            QMessageBox.warning(self, "Aviso", "Informe um email válido.")
            return

        agora = datetime.now()
        item = {
            "id": agora.isoformat(),
            "tipo": self.opcao,
            "texto": texto,
            "email": email,
            "data": agora.strftime("%d/%m/%Y"),
        }
        caminho_anexo_salvo = ""
        try:
            if self.anexo_selecionado:
                pasta_anexos = os.path.join(PASTA_DADOS, "anexos_feedback")
                os.makedirs(pasta_anexos, exist_ok=True)
                nome_arquivo = (
                    f"{uuid.uuid4().hex}{os.path.splitext(self.anexo_selecionado)[1]}")
                caminho_anexo_salvo = os.path.join(pasta_anexos, nome_arquivo)
                shutil.copy2(self.anexo_selecionado, caminho_anexo_salvo)
                item["anexo"] = os.path.join("anexos_feedback", nome_arquivo)

            todos = ler_json(FICHEIRO_FEEDBACK, [])
            todos.append(item)
            gravar_json(FICHEIRO_FEEDBACK, todos)
        except OSError as erro:
            if caminho_anexo_salvo and os.path.exists(caminho_anexo_salvo):
                try:
                    os.remove(caminho_anexo_salvo)
                except OSError as erro_limpeza:
                    QMessageBox.warning(
                        self, "Aviso",
                        f"Não foi possível limpar o anexo temporário:\n{erro_limpeza}")
            QMessageBox.critical(self, "Erro", f"Não foi possível guardar o feedback:\n{erro}")
            return

        self.mostrar_feedback(item)
        QMessageBox.information(self, "Sucesso", "Feedback registado!")
        self.anexo_selecionado = ""
        self.nome_anexo.clear()
        self.btn_remover_anexo.hide()
        self.chat_box.hide()

    # ---------- feedback ----------
    def mostrar_feedback(self, item):
        caixa = QFrame()
        caixa.setObjectName("FeedbackItem")
        layout = QVBoxLayout(caixa)
        layout.setContentsMargins(5, 3, 5, 5)
        layout.setSpacing(2)

        linha = QWidget()
        h = QHBoxLayout(linha)
        h.setContentsMargins(0, 0, 0, 0)
        tipo = str(item.get("tipo", "Feedback"))
        data = str(item.get("data", ""))
        resumo = QToolButton()
        resumo.setObjectName("FeedbackToggle")
        resumo.setText(f"{tipo}  ·  {data}")
        resumo.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        resumo.setArrowType(Qt.RightArrow)
        resumo.setCheckable(True)
        resumo.setCursor(Qt.PointingHandCursor)

        lixo = QPushButton("🗑")
        lixo.setObjectName("DeleteFeedback")
        lixo.setFixedSize(24, 24)
        lixo.setCursor(Qt.PointingHandCursor)
        lixo.clicked.connect(partial(self.apagar_feedback, item, caixa))

        h.addWidget(resumo, 1)
        h.addWidget(lixo, 0, Qt.AlignTop)
        layout.addWidget(linha)

        detalhes_texto = html.escape(str(item.get("texto", ""))).replace("\n", "<br>")
        email = html.escape(str(item.get("email", "Não informado")))
        detalhes = QLabel(f"<b>Email:</b> {email}<br><b>Mensagem:</b><br>{detalhes_texto}")
        detalhes.setObjectName("FeedbackDetails")
        detalhes.setWordWrap(True)
        detalhes.setTextFormat(Qt.RichText)
        detalhes.hide()
        layout.addWidget(detalhes)

        caminho_anexo = item.get("anexo")
        if caminho_anexo:
            nome_arquivo = html.escape(os.path.basename(str(caminho_anexo)))
            anexo_label = QLabel(f"<b>Anexo:</b> {nome_arquivo}")
            anexo_label.setObjectName("FeedbackDetails")
            anexo_label.hide()
            layout.addWidget(anexo_label)

            abrir_anexo = QPushButton("Abrir anexo")
            abrir_anexo.setObjectName("OpenAttachment")
            abrir_anexo.setCursor(Qt.PointingHandCursor)
            abrir_anexo.hide()
            abrir_anexo.clicked.connect(partial(self.abrir_anexo, caminho_anexo))
            layout.addWidget(abrir_anexo)
        else:
            anexo_label = None
            abrir_anexo = None

        resumo.toggled.connect(
            partial(self.alternar_detalhes_feedback, resumo, detalhes,
                    anexo_label, abrir_anexo)
        )
        self.lista_layout.addWidget(caixa)

    @staticmethod
    def alternar_detalhes_feedback(resumo, detalhes, anexo_label,
                                   abrir_anexo, expandido):
        detalhes.setVisible(expandido)
        if anexo_label is not None:
            anexo_label.setVisible(expandido)
            abrir_anexo.setVisible(expandido)
        resumo.setArrowType(Qt.DownArrow if expandido else Qt.RightArrow)

    def abrir_anexo(self, caminho_anexo):
        caminho = os.path.join(PASTA_DADOS, caminho_anexo)
        if not os.path.isfile(caminho):
            QMessageBox.warning(self, "Anexo não encontrado",
                                f"O arquivo anexado não foi encontrado:\n{caminho}")
            return
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(caminho)):
            QMessageBox.warning(self, "Erro", "Não foi possível abrir o anexo.")

    def apagar_feedback(self, item, caixa):
        confirmacao = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f"Deseja excluir este feedback?\n\n"
            f"{item.get('tipo', 'Feedback')} · {item.get('data', '')}\n"
            "Esta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirmacao != QMessageBox.Yes:
            return

        try:
            restantes = [f for f in ler_json(FICHEIRO_FEEDBACK, []) if f.get("id") != item.get("id")]
            gravar_json(FICHEIRO_FEEDBACK, restantes)
        except OSError as erro:
            QMessageBox.critical(self, "Erro", f"Não foi possível apagar:\n{erro}")
            return

        caminho_anexo = item.get("anexo")
        if caminho_anexo:
            arquivo_anexo = os.path.join(PASTA_DADOS, caminho_anexo)
            try:
                if os.path.isfile(arquivo_anexo):
                    os.remove(arquivo_anexo)
            except OSError as erro:
                QMessageBox.warning(
                    self, "Aviso",
                    f"O feedback foi apagado, mas não foi possível remover o anexo:\n{erro}")

        self.lista_layout.removeWidget(caixa)
        caixa.deleteLater()
        QMessageBox.information(self, "Sucesso", "Feedback apagado com sucesso!")

    # ---------- posição do chat ----------
    def posicionar_chat(self):
        margem = 15
        self.chat_btn.move(self.width() - self.chat_btn.width() - margem,
                           self.height() - self.chat_btn.height() - margem - 10)
        self.chat_box.move(self.width() - self.chat_box.width() - margem,
                           self.chat_btn.y() - self.chat_box.height() - 8)

    def resizeEvent(self, evento):
        self.posicionar_chat()
        super().resizeEvent(evento)
        self.atualizador_grade.start(80)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    janela = Launcher()
    janela.show()
    sys.exit(app.exec())