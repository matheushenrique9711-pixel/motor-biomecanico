# 🚀 Quick Start - Deployment em 5 Passos

## Passo 1: Push para GitHub
```bash
cd /caminho/para/motor-biomecanico

git init
git add .
git commit -m "Initial: Motor Biomecânico"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/motor-biomecanico.git
git push -u origin main
```

**Use seu Personal Access Token (GitHub → Settings → Developer settings → Personal access tokens)**

---

## Passo 2: Criar Banco de Dados no Railway

1. Vá em https://railway.app
2. Sign up com GitHub
3. Clique **Create New Project** → **Provision PostgreSQL**
4. Copie a `DATABASE_URL`

---

## Passo 3: Adicionar Backend ao Railway

No mesmo projeto:
1. Clique **+ New** → **GitHub Repo**
2. Selecione seu repositório
3. Configure Root Directory: `.`
4. Adicione variável: `DATABASE_URL` = [URL que copiou]
5. Clique **Deploy**

Espere o deploy terminar e copie a **Public URL** do backend

---

## Passo 4: Deployar Frontend no Vercel

1. Vá em https://vercel.com
2. Clique **Import Project**
3. Selecione seu repositório GitHub
4. Configure:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Output Directory:** `dist`
5. Clique **Environment Variables** e adicione:
   ```
   REACT_APP_API_URL = https://seu-backend-railway.app/api
   ```
   (Use a URL do Railway do passo 3)
6. Clique **Deploy**

---

## Passo 5: Pronto! 🎉

Acesse:
- **Frontend:** `https://seu-frontend.vercel.app`
- **API:** `https://seu-backend-railway.app/api/presets/`

---

## Atualizações Futuras

```bash
# Quando precisar atualizar:
git add .
git commit -m "Descrição da mudança"
git push origin main

# Vercel e Railway redeployam automaticamente em 2 minutos!
```

---

**Tempo total: 20 minutos**  
**Custo: GRATUITO (planos free)**  
**Funciona em: Mac, iPhone, Windows, Android**
