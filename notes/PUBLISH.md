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

## PWA — abre sem sinal e se atualiza sozinha (v4)

O mesmo build gera duas saídas:
- `dist/index.html` → **Artifact no claude.ai** (a única com revisão do Claude; precisa de internet e login).
- `docs/` → **PWA** para GitHub Pages: `index.html` + `sw.js` (service worker, cache do app) + `manifest.webmanifest` + ícones. Instala na tela inicial, **abre offline**, e quando há internet busca a versão nova e recarrega sozinha (toast "Updated…").

### Publicar a PWA (fluxo para o Opus 5)
```bash
cd ~/Downloads/Airbnb-Trainer
python3 build.py          # gera dist/ e site/ com carimbo de build novo
git add -A && git commit -m "build: <o que mudou>"
git push                  # GitHub Pages publica docs/ em ~1 min
```
O `sw.js` muda de nome de cache a cada build (`elevated-line-<build>`), então o celular detecta a atualização na próxima abertura com internet.

### Primeira vez (uma vez só)
1. `gh auth login` (o Daniel faz, no terminal dele — abre o navegador).
2. `gh repo create elevated-line --private --source . --push` — **privado não serve para Pages no plano gratuito**; se for gratuito, usar `--public` (o conteúdo é fictício e não há chaves).
3. Ligar Pages: `gh api -X POST repos/<user>/elevated-line/pages -f build_type=legacy -f "source[branch]=main" -f "source[path]=/site"`.
4. URL: `https://<user>.github.io/elevated-line/` → no S24: Chrome → ⋮ → **Instalar app**.

### No celular
- Instale a PWA e abra uma vez **com internet** (é quando o cache é criado). Depois abre sem sinal.
- O botão **Online** dentro da PWA abre a versão do claude.ai (Claude review). O progresso é separado entre as duas.
- Vozes: Me → Voices; instale as vozes Google em Ajustes → Conversão de texto em voz.
