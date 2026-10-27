# Power BI Launcher

Launcher simples em Python + PySide6 que reúne os links dos teus dashboards Power BI num só sítio e abre-os com um clique, com um chat integrado para sugestões de melhoria e reporte de erros. O acesso a cada dashboard continua a ser controlado pelo Power BI.

A interface usa tema escuro com as cores `#055f6b` e `#c2ce45`. A logo em
`Public/Logo - Ge.png` aparece no canto superior esquerdo da janela.
Também permite buscar dashboards pelo nome, exibe a data de atualização cadastrada
e mostra os detalhes dos feedbacks ao expandir cada item. A grade de BI adapta
automaticamente o número de colunas ao tamanho da janela e ordena todos os BI
alfabeticamente em uma única grade, sem agrupá-los por setor.
No assistente, é possível anexar imagens e documentos ao feedback. Os arquivos
ficam em `dados/anexos_feedback/` e são removidos quando o feedback é excluído.

## Como correr

```
pip3 install PySide6
python3 app.py
```

A app lê `dados/dashboards.json` quando esse ficheiro existe. Se ainda não existir,
usa `dados/dashboards.exemplo.json` automaticamente. Podes editar o exemplo diretamente
ou copiá-lo para `dashboards.json` para manter uma configuração própria.

## Onde ficam os dados

A app guarda tudo em ficheiros JSON, dentro de uma pasta `dados/`:

- `dashboards.json`: a lista de dashboards que aparecem nos cards (opcional; se não existir, é usado `dashboards.exemplo.json`).
- `feedback.json`: o feedback enviado pelo chat (é criado automaticamente).

Se nem `dashboards.json` nem `dashboards.exemplo.json` existirem, a app mostra um aviso a pedir para configurares os dashboards.

### Exemplo de `dashboards.json`

```json
[
  {
    "nome": "Vendas",
    "setor": "Comercial",
    "link": "https://app.powerbi.com/...",
    "icone": "📈",
    "pre_visualizacao": "Public/previews/vendas.png",
    "data_atualizacao": "2026-10-20"
  }
]
```

`nome` e `link` são obrigatórios. `setor`, `icone`, `pre_visualizacao` e
`data_atualizacao` são opcionais. A miniatura deve ser uma imagem local, com caminho
relativo à pasta do app (por exemplo, `Public/previews/vendas.png`); ela substitui o
ícone no card. Se não houver uma imagem válida, o card mostra `icone`. O setor é
exibido quando preenchido. `data_atualizacao` usa o formato `AAAA-MM-DD`; sem uma
data válida, a interface indica que a atualização não foi informada. JSONs existentes
com os campos `url`, `emoji` e `data` continuam funcionando.

## Permissões e acessos

O launcher não gere permissões. Cada card é só um atalho que abre o link do dashboard no browser, e quem controla o acesso é o próprio Power BI.

Quando alguém clica num card, o Power BI verifica na página web se essa pessoa tem permissão para ver o relatório. Se tiver, o dashboard abre. Se não tiver, o Power BI bloqueia o acesso e mostra a mensagem de permissão negada.

Isto significa que:

- Não é preciso configurar utilizadores nem permissões na app.
- Ter o launcher não dá acesso a nada que a pessoa não pudesse ver antes.
- Para dar ou retirar acesso a um dashboard, altera-se a partilha no Power BI (workspace, relatório ou app), não o `dashboards.json`.
- O `dashboards.json` só guarda os links, não guarda dados dos relatórios nem credenciais.

## Usar num servidor interno (recomendado)

Por defeito os ficheiros ficam na pasta `dados/` ao lado do `app.py`, ou seja, cada pessoa tem o seu feedback local, espalhado pelos vários computadores.

Para uma utilização em equipa, o recomendado é colocar a pasta de dados num servidor interno da empresa e indicar o caminho com a variável de ambiente `LAUNCHER_DADOS`. Isto torna a solução mais segura e mais fácil de gerir:

- **Controlo de acesso:** as permissões da pasta no servidor definem quem pode ler e quem pode editar. Por exemplo, todos podem ler o `dashboards.json`, mas só a equipa de TI o pode alterar.
- **Dados dentro da rede:** o feedback (que inclui emails) fica guardado no servidor interno e não em cópias soltas nos computadores dos utilizadores.
- **Um só sítio para manter:** editas o `dashboards.json` uma vez e todos veem a mudança.
- **Cópias de segurança:** a pasta passa a fazer parte do backup normal do servidor.

Mac / Linux:
```
export LAUNCHER_DADOS="/Volumes/Partilha/launcher"
python3 app.py
```

Windows (PowerShell):
```
$env:LAUNCHER_DADOS = "\\servidor\partilha\launcher"
python app.py
```

Nota: a segurança vem das permissões do servidor, não da app. O launcher não faz autenticação própria.

## Limitações

- O feedback fica num ficheiro de texto. Se duas pessoas enviarem ao mesmo tempo, uma pode sobrepor a outra (para uso pequeno chega; para mais, o próximo passo seria uma base de dados).
- Apagar feedback pede confirmação. Isto não é controlo de acesso: numa pasta partilhada, as permissões devem ser geridas no servidor.