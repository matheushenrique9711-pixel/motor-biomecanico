# Motor Biomecânico - Guia de Deployment

## 🚀 Deployment Automático (Vercel + Railway)

Este guia mostra como deployar o Motor Biomecânico em produção com acesso via URL pública.

**Tempo estimado:** 20 minutos  
**Custo:** Gratuito (planos free do Vercel e Railway)

---

## 📋 Pré-requisitos

1. ✅ Conta GitHub (você já tem)
2. ✅ Conta Vercel (conecta com GitHub)
3. ✅ Conta Railway (para banco de dados PostgreSQL)

---

## 🔧 Passo 1: Preparar o Repositório GitHub

### 1.1 Criar um repositório privado no GitHub

1. Vá para **https://github.com/new**
2. **Repository name:** `motor-biomecanico`
3. **Description:** Sistema de Palmilhas Ortopédicas 3D
4. **Private** ✅ (selecione como privado)
5. **Clique em "Create repository"**

### 1.2 Fazer push do código

Na sua pasta local onde está o projeto:

```bash
cd /caminho/para/motor-biomecanico

# Inicializar git (se ainda não estiver)
git init

# Adicionar todos os arquivos
git add .

# Criar primeiro commit
git commit -m "Initial commit: Motor Biomecânico com 10 presets"

# Adicionar remote do GitHub (substitua SEU_USUARIO pelo seu)
git remote add origin https://github.com/SEU_USUARIO/motor-biomecanico.git

# Fazer push
git branch -M main
git push -u origin main
```

Se pediu senha, use um **Personal Access Token** (não senha):
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Gere um novo token com permissões: `repo`, `admin:repo_hook`
3. Cole o token quando pedir senha

---

## 🎯 Passo 2: Configurar Railway (Banco de Dados)

### 2.1 Criar projeto no Railway

1. Vá para **https://railway.app**
2. **Sign up** com GitHub (usa sua conta)
3. Clique em **Create New Project**
4. Selecione **Provision PostgreSQL**
5. Nomeie como `motor-biomecanico-db`

### 2.2 Obter credenciais

1. No dashboard do Railway, clique no banco PostgreSQL
2. Vá em **Connect**
3. Copie a string: `DATABASE_URL` (PostgreSQL)
4. Guarde essa string (vai usar no Vercel para o backend)

### 2.3 Adicionar o Backend

1. No mesmo projeto Railway:
2. Clique em **+ New** → **GitHub Repo**
3. Selecione seu repositório `motor-biomecanico`
4. Configure:
   - **Root Directory:** `.` (raiz)
   - **Environment:** Production
5. Clique em **Deploy**

### 2.4 Configurar variáveis de ambiente do Backend

No painel do Railway, na seção Variables:

```
DATABASE_URL = [copie da conexão PostgreSQL acima]
CORS_ORIGINS = ["https://seu-frontend.vercel.app"]
ENVIRONMENT = production
```

🎯 **Copie a URL do backend** (aparece em "Public URL" no Railway) - vai precisar no Vercel

---

## 🌐 Passo 3: Configurar Vercel (Frontend)

### 3.1 Conectar repositório ao Vercel

1. Vá para **https://vercel.com**
2. Clique em **Import Project**
3. **Importar do GitHub** → selecione `motor-biomecanico`
4. Configure:
   - **Framework Preset:** Other
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Output Directory:** `dist`

### 3.2 Configurar variáveis de ambiente

Antes de fazer deploy, adicione:

```
REACT_APP_API_URL = https://seu-backend-railway.railway.app/api
```

(Substitua pela URL que copou do Railway)

### 3.3 Fazer Deploy

Clique em **Deploy** e espere (2-3 minutos)

---

## ✅ Verificar se tudo funciona

### 1. Testar o Frontend
```
https://seu-frontend.vercel.app
```
Deve abrir o Dashboard do Motor Biomecânico

### 2. Testar a API
```
https://seu-backend-railway.railway.app/api/presets/
```
Deve retornar um JSON com os 10 presets

### 3. Testar no seu Mac/iPhone/Windows
- Abra o navegador
- Digite a URL do Vercel
- Deve funcionar em qualquer dispositivo! ✅

---

## 🔄 Atualizações Automáticas

Depois que tudo está deployado, as atualizações são **automáticas**:

### Para fazer uma atualização:

1. **No seu computador local:**
```bash
cd motor-biomecanico

# Fazer suas mudanças nos arquivos

# Commit e push
git add .
git commit -m "Descrição da mudança"
git push origin main
```

2. **Vercel e Railway detectam automaticamente** o push e redeployam em ~2 minutos ✅

### Não precisa fazer mais nada! O sistema atualiza sozinho.

---

## 📱 Acessar de qualquer dispositivo

Com tudo deployado, você acessa de:

### MacBook
```
https://seu-frontend.vercel.app
```

### iPhone/iPad
```
https://seu-frontend.vercel.app
```
(Funciona perfeitamente em Safari)

### Windows PC
```
https://seu-frontend.vercel.app
```
(Funciona em Edge, Chrome, Firefox)

### Salvar como atalho
- **iPhone:** Safari → Share → Add to Home Screen
- **Android:** Chrome → Menu → "Install app"
- **Mac:** Cmd+Shift+B (favoritos) ou criar atalho

---

## 🆘 Troubleshooting

### "Frontend não carrega"
```bash
# Verifique no Vercel:
# 1. Vá em https://vercel.com/seu-usuario/motor-biomecanico
# 2. Clique em último deploy
# 3. Veja os logs de erro em "Build Log"
```

### "API retorna erro 500"
```bash
# Verifique no Railway:
# 1. Vá em https://railway.app
# 2. Clique no seu backend
# 3. Veja os logs em "Logs"
# 4. Verifique se DATABASE_URL está correto
```

### "Presets não aparecem"
```bash
# No Railway, execute as migrations:
# 1. Vá em seu backend
# 2. Clique em "Deployments"
# 3. Abra o último deploy
# 4. Verifique se rodou: "python -m alembic upgrade head"
```

---

## 📞 URLs finais

Depois de pronto, você terá:

| Serviço | URL |
|---------|-----|
| **Frontend** | https://seu-frontend.vercel.app |
| **Backend API** | https://seu-backend-railway.railway.app/api |
| **API Docs** | https://seu-backend-railway.railway.app/docs |
| **Banco de Dados** | Gerenciado pelo Railway (privado) |

---

## 💡 Dicas importantes

✅ **Backup**: Railway e Vercel fazem backup automático  
✅ **Segurança**: Banco de dados é privado, acesso via API só  
✅ **Escalabilidade**: Se crescer, é fácil escalar no Railway/Vercel  
✅ **Monitoramento**: Ambos oferecem logs em tempo real  
✅ **Custom Domain**: Depois você adiciona um domínio próprio em ambos

---

## 🎓 Próximos passos

1. **Teste tudo** em diferentes dispositivos
2. **Adicione um domínio customizado** (opcional):
   - motor-biomecanico.com no Vercel
   - api.motor-biomecanico.com no Railway
3. **Configure um email de contato** nos settings
4. **Compartilhe a URL** com sua equipe da clínica

---

**Sistema pronto para produção!** 🚀

---

*Última atualização: 2026-09-28*  
*Motor Biomecânico v1.0*
