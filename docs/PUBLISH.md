# Publicação

**Artifact (privado):** https://claude.ai/code/artifact/025fdbf5-a9fc-41e5-84a3-71aff5161ad2
Publicado em 2026-09-11 (v1 — Fable build). Capacidade declarada: `sample`.

## Republicar depois de editar

1. `python3 build.py` (na pasta `Airbnb-Trainer/`)
2. No Claude Code, ferramenta **Artifact**:
   - `file_path`: `/Users/danieloliveira/Downloads/Airbnb-Trainer/dist/index.html`
   - `url`: a URL acima (obrigatório fora desta conversa, senão cria outro artifact)
   - `capabilities`: omitir (mantém `sample`) — ou `{"sample": {}}` para redeclarar
   - `favicon`: omitir (mantém 📞)
   - `label`: uma etiqueta curta da versão (ex.: "v2 — cenários de host")
3. Antes de publicar de outra conversa, fazer `action: "read"` com a `url`
   (o publish exige que a conversa tenha lido a versão atual).

## No celular (S24 Ultra)

1. Abrir a URL no **Chrome** logado na conta do Claude.
2. Menu ⋮ → **Adicionar à tela inicial** (vira ícone; abre em tela cheia).
3. Na primeira chamada online, o Claude pede consentimento uma vez.
4. Vozes: Ajustes do Android → Gerenciamento geral → Conversão de texto em
   voz → Google → instalar dados de voz para **English (India)**,
   **(United Kingdom)**, **(Australia)**, **(Nigeria)**, **(South Africa)**,
   **(Ireland)** — assim os sotaques dos cenários funcionam offline.

## O que NÃO fazer

- Não tornar público pelo menu de compartilhamento.
- Não adicionar chaves de API ao código (não é necessário: `sample` usa a
  conta do visualizador).
