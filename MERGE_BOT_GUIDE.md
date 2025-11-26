# 🤖 Merge Bot Guide

Estilo PyTorch! Use comandos de comentário para mergear PRs.

## Como Usar

### Opção 1: Mencionar o bot

Comente no PR:

```
@mergebot merge
```

ou

```
@merge-bot merge
```

### Opção 2: Comando simples

Comente no PR:

```
/merge
```

ou simplesmente:

```
merge
```

## O que acontece

1. **Bot reage com 🚀** - Mostra que está processando
2. **Verifica permissões** - Só colaboradores com acesso write/admin podem mergear
3. **Verifica se PR está pronto** - Não pode ser draft, não pode ter conflitos
4. **Aguarda checks** - Espera até 10 minutos por CI, testes, CodeQL, etc.
5. **Faz merge** - Usa squash merge
6. **Deleta branch** - Remove branch automaticamente
7. **Bot reage com 👍** - Confirma sucesso

## Exemplo Completo

```
# Você comenta:
@mergebot merge

# Bot responde com emoji 🚀

# Bot aguarda CI passar...

# CI passa ✅

# Bot comenta:
✅ PR merged successfully by @seu-usuario!

# Bot adiciona emoji 👍 no seu comentário
```

## Requisitos

- ✅ Você deve ter acesso de **write** ou **admin** no repo
- ✅ PR não pode ser draft
- ✅ PR não pode ter conflitos
- ✅ Todos os checks devem passar (ou bot aguarda até 10min)

## Mensagens de Erro

### ❌ Sem permissão

```
❌ @usuario you don't have permission to merge PRs.
Only collaborators with write access can use merge commands.
```

**Solução**: Peça a um maintainer para mergear.

### ❌ PR é draft

```
❌ Cannot merge: PR is still a draft.
Please mark it as ready for review first.
```

**Solução**: Clique em "Ready for review" no PR.

### ❌ Conflitos

```
❌ Cannot merge: PR has conflicts or is not mergeable.
Please resolve conflicts first.
```

**Solução**: Resolva os conflitos manualmente.

### ❌ Checks falharam

```
❌ Cannot merge: The following checks failed:

- ❌ Ruff Lint & Format
- ❌ Test Python 3.10

Please fix the issues and try again.
```

**Solução**: Corrija os erros e faça push novamente.

### ⏱️ Timeout

```
⏱️ Timeout waiting for checks to complete (waited 10 minutes).

You can try the merge command again once checks complete.
```

**Solução**: Aguarde checks completarem e tente novamente.

## Comparação com Auto-Merge

| Feature | Auto-Merge (label) | Merge Bot (comando) |
|---------|-------------------|---------------------|
| Como ativar | Adicionar label `automerge` | Comentar `@mergebot merge` |
| Quando merge | Automaticamente quando CI passa | Quando você pedir explicitamente |
| Bom para | Dependabot, PRs triviais | PRs que precisam review manual |
| Controle | Automático | Manual (você escolhe quando) |

## Quando Usar Cada Um

### Use Auto-Merge (label) para:
- ✅ PRs do Dependabot
- ✅ Pequenas mudanças de docs
- ✅ Fixes triviais

### Use Merge Bot (comando) para:
- ✅ PRs grandes que você reviewou
- ✅ Quando quer controle explícito
- ✅ Quando precisa aguardar algo específico

## Comandos Suportados

Todas essas variações funcionam:

```bash
@mergebot merge
@merge-bot merge
/merge
merge
```

(Case-insensitive, espaços extras são ignorados)

## Segurança

- 🔒 Só colaboradores com **write access** podem usar
- 🔒 Verifica branch protection rules
- 🔒 Aguarda todos os checks obrigatórios
- 🔒 Não pode mergear PRs com conflitos
- 🔒 Não pode mergear drafts

## Exemplos de Uso

### Exemplo 1: Review + Merge

```markdown
# Você reviewa o PR, aprova

# Depois comenta:
LGTM! @mergebot merge

# Bot faz o resto
```

### Exemplo 2: Aguardar CI

```markdown
# CI ainda rodando...

# Você comenta:
@mergebot merge

# Bot aguarda CI terminar (até 10min)
# Se passar, faz merge automaticamente
```

### Exemplo 3: Tentar novamente após fix

```markdown
# CI falhou, você fixou

# Comenta:
Fixed! /merge

# Bot aguarda novo CI passar e faz merge
```

## Dicas

💡 **Combine com reviews**: Aprove o PR e use `@mergebot merge` no mesmo comentário

💡 **Use em qualquer comentário**: Não precisa ser o último, bot detecta em qualquer comentário

💡 **Bot é patient**: Aguarda até 10 minutos por checks, não precisa ficar esperando

💡 **Falhou? Tente de novo**: Se algo deu errado, basta comentar novamente

## Troubleshooting

### Bot não respondeu

1. Verifique se comentou **no PR** (não em issue)
2. Verifique se usou um dos comandos corretos
3. Verifique logs em Actions → Merge Bot

### Bot falhou

Veja o log do workflow:
```bash
gh run list --workflow="Merge Bot" --limit 5
gh run view <RUN_ID> --log
```

## Configuração

Workflow: `.github/workflows/merge-bot.yml`

Para modificar:
- Tempo de espera (padrão: 10 minutos)
- Merge method (padrão: squash)
- Comandos aceitos
- Permissões necessárias
