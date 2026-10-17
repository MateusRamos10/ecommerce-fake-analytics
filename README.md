# volta: loja fake de eletrônicos

E-commerce **fictício** criado para um projeto de portfólio de web analytics. Nenhum produto é vendido e nenhum dado de pagamento é real.

## Rodar localmente

```bash
cd site
python3 -m http.server 8000
# abra http://localhost:8000
```

É necessário um servidor, pois o `products.json` é carregado via `fetch`.

## Estrutura

- `site/`: tudo que é publicado (HTML, CSS, JS, assets)
- `identity_example/`: imagens de referência de estilo (não vão para o site)
- `VERSION` e `site/version.json`: versão do site (devem ter o mesmo valor)
- `CHANGELOG.md`: histórico de versões

## Imagens a substituir

Mantenha o mesmo nome de arquivo; nenhum código precisa mudar.

| Arquivo | Formato recomendado |
|---|---|
| `site/assets/logo.svg` | SVG, altura ~28 px |
| `site/assets/favicon.svg` | SVG quadrado |
| `site/assets/products/p01.webp` a `p12.webp` | WebP quadrado, ~800x800 px, até ~150 KB |

## Versionar

1. Atualize `VERSION` e `site/version.json`.
2. Registre a mudança no `CHANGELOG.md`.
3. Commit (Conventional Commits: `feat:`, `fix:`, `docs:`, `chore:`).
4. `git tag vX.Y.Z` e `git push --tags`.

## Publicar na Vercel

Importe o repositório do GitHub e configure **Root Directory = `site`**, sem comando de build e sem framework.
