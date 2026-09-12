# Elevated Line — simulador de atendimento (Airbnb Elevated Support)

App de treino de chamadas em inglês, mobile-first (Samsung S24 Ultra), com
biblioteca offline e modo online via Claude. **Construído com Fable 5.1;
mantido com Opus 5** — por isso tudo é arquivo de texto simples e o
conteúdo fica separado do código.

## Estrutura

```
Airbnb-Trainer/
  index.html          ← o app (template, ASCII-only). Motor em JS puro, sem framework.
  build.py            ← inlina content/*.json no template → dist/index.html
  content/
    scenarios.json    ← cenários com turnos, respostas-modelo, coach (offline)
    emotions.json     ← matriz de soft skills (23 estados emocionais)
    phrases.json      ← banco de frases por fase da chamada (20 fases)
    policies.json     ← referência DERIVADA do Help Center (com URLs)
    rubric.json       ← rubrica de correção (11 dimensões, 3 críticas, red flags)
    drills.json       ← 30 drills de escuta por sotaque
    vocab.json        ← espelho do baralho Anki (tag airbnb)
    ops.json          ← REGRAS DA OPERAÇÃO (auth, gravação, sumarização, holds, imparcialidade) — não é Help Center
  dist/index.html     ← arquivo publicado como Artifact no claude.ai (gerado)
  site/               ← PWA para GitHub Pages: index.html + sw.js + manifest + ícones (gerado; versionado)
  sw.js, manifest.webmanifest, icon-*.png ← fontes da PWA (build.py carimba e copia para site/)
  docs/               ← notas
```

## As 12 fases e as 3 regras que demitem

`opening → auth → recording → listen → paraphrase → empathy → clarify → policy → options → summary → confirm → close`

Críticas (falha = nota limitada a 8/24 e banner de reprovação):
- **auth** — três caminhos: Alura (nome e sobrenome) · PIN no número verificado · manual (nome completo, telefone, data de nascimento, **4 últimos** dígitos do pagamento). Nunca senha, cartão completo, CVV.
- **recording** — em todo callback/outbound: "gravada para treinamento e qualidade — tudo bem?"; se não, pode parar a gravação.
- **summary** — antes de "os passos ficaram claros?" e "mais alguma coisa?" e de "vou fechar o caso": resumir TUDO.

Outras regras (em `content/ops.json`): parafrasear o problema; até **2 holds × 3 min** com permissão; transferir para chat com permissão; imparcial com inclinação ao guest, sem pagar injustiça, sem perder cliente de alto valor; CSAT máximo por personalização.

## v4 — PWA offline com auto-atualização; Hold removido

- `site/` é uma PWA: service worker com cache do app (abre sem sinal) e auto-atualização ao reconectar (`reg.update()` no evento `online`, `skipWaiting` + reload). Deploy = `git push` (GitHub Pages serve `site/`). Ver `docs/PUBLISH.md`.
- O Claude só existe na versão do claude.ai (`dist/`); na PWA o botão Online abre esse link.
- O botão de Hold foi removido da chamada a pedido do Daniel (a regra continua documentada em `ops.json`/frases como conhecimento).

## v3 — modo, surpresa, vozes, ASCII

- **Offline é o padrão** (zero chamadas ao Claude). O botão **Offline | Online** no topo troca; a preferência fica no aparelho. Online usa o nível `quick` (configurável em Me → "Claude review depth"); gerar cenário usa `complex`.
- **Chamadas de surpresa:** a aba Calls tem "Take the next incoming call" e "Make a callback from the queue" — sorteio ponderado (cenários menos treinados vêm mais). Em inbound, o chamador é "Unknown caller" e o **arquivo do caso só destrava depois da fase auth**; em callback ele já vem aberto. Título, categoria e emoção só aparecem no debrief. A lista com filtros continua em Me → Practice library.
- **Vozes:** escolha ranqueada por qualidade (Google > neural > local; eSpeak/compact penalizadas), texto falado em frases (Android corta falas longas), velocidade padrão **0,92**, seletor na chamada, e **Me → Voices** para fixar a voz de cada sotaque no aparelho.
- **ASCII puro:** `build.py` escapa o JSON (`ensure_ascii=True`) e o template não tem caracteres não-ASCII — imune a problemas de charset. Bandeiras viraram códigos (GB, US, IN…).

## Como funciona

- **Offline** (sempre): cenários roteirizados com ramificação (fala do cliente
  muda se a resposta anterior foi fraca), banco de frases, políticas, drills,
  vocabulário. O cliente **fala** com a síntese de voz do Android no sotaque
  do cenário. A correção offline é **heurística** (checa fases e red flags) e
  se declara como tal na tela.
- **Online** (quando `claude.use("sample")` resolve): a resposta do agente é
  avaliada na rubrica completa, com reescrita natural e correções de inglês;
  depois dos turnos roteirizados dá para **improvisar** com o Claude fazendo o
  cliente; e dá para **gerar cenários novos** com os filtros e o léxico.
  Usa a conta do visualizador via capacidade `sample` — **não existe chave de
  API em lugar nenhum** e não deve existir nunca.
- **Microfone**: transcrição usa a Web Speech API (precisa de internet). Se o
  navegador bloquear o microfone dentro do visualizador, o app cai para
  "digitar" e avisa. A síntese de voz não depende disso.
- **Progresso** fica em `localStorage` no aparelho. Nada sai do telefone.

## Editar conteúdo (Opus 5)

1. Edite o JSON certo em `content/`. Esquemas estão descritos no `_about` de
   cada arquivo; para cenários, copie um existente e mude.
2. `python3 build.py` (ou `python3 build.py --vocab-from-anki` com o Anki
   aberto, para puxar palavras novas do baralho).
3. Republicar: no Claude Code, chamar a ferramenta **Artifact** com
   `file_path: dist/index.html` e a **mesma `url`** do artifact existente
   (ver `docs/PUBLISH.md`). Passar `capabilities: {"sample": {}}` se for
   redeclarar; omitir mantém.

### Esquema de cenário (resumo)

```json
{"id":"acc-in-01","title":"…","category":"access|uninhabitable|mismatch|host_cancel|guest_cancel|host_damage|appeal|repeat_contact",
 "callType":"inbound_guest|inbound_host|outbound_guest|outbound_host","severity":1,"emotion":"<id em emotions.json>","accent":"en-GB|en-US|en-AU|en-IN|en-IE|en-ZA|en-NG",
 "caller":{"name":"…","role":"guest|host"},
 "auth":{"path":"alura|pin|manual","customer_name":"…","verified_phone_ends":"4471","pin":"829153","phone":"…","dob":"…","payment_last4":"…"},
 "callback":false,"value_tier":"high|standard","reference":"4471",
 "context":{"listing":"…","booking":"…","policy":"…","facts":["…"]},
 "lexicon":["palavras que o cliente vai usar"],
 "turns":[{"customer":"fala","expects":["opening","verify","empathy"],"model":"resposta-modelo com {name}","coach":"nota em PT","customer_if_weak":"fala escalada"}],
 "resolution":{"correct":"…","policy_ref":"<id em policies.json>","why":"…"}}
```
Fases válidas em `expects`: opening, auth, recording, listen, paraphrase,
empathy, clarify, policy, options, summary, confirm, close — mais os extras
ownership, expectations, future. Todo cenário precisa de um turno com `auth`
e um turno final com `summary`,`confirm`,`close`.

## Segurança (regras do projeto)

- Nunca colocar chave de API, token ou dado pessoal no código ou no conteúdo.
- O artifact nasce **privado**; não tornar público (os cenários contêm nomes
  fictícios, mas o app é ferramenta pessoal de treino).
- Conteúdo de política é **paráfrase com link**; não copiar texto do Help
  Center para dentro do app.
- O app nunca pede senha, número completo do cartão ou CVV — a rubrica
  reprova isso como falha crítica (`sensitive_data`). Os **4 últimos dígitos**
  do método de pagamento são permitidos e exigidos na autenticação manual.

## Ideias já previstas, ainda não feitas

- Nota de pronúncia por fonema (Azure Speech / Speechace) — decisão à parte.
- Áudios humanos do Speech Accent Archive (GMU) para sotaques que a TTS não
  cobre (jamaicano, holandês).
- Exportar palavras novas dos cenários gerados direto para o Anki.
