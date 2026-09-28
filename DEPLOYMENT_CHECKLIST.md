# ✅ Deployment Checklist

## GitHub Setup
- [ ] Criar repositório privado `motor-biomecanico`
- [ ] Gerar Personal Access Token (Settings → Developer settings)
- [ ] Fazer `git push` com o token
- [ ] Verificar que os arquivos estão no repositório

## Railway Setup (Banco de Dados + Backend)
- [ ] Criar conta no Railway (com GitHub)
- [ ] Provisionar PostgreSQL
- [ ] Copiar `DATABASE_URL` da conexão
- [ ] Adicionar Backend via GitHub Repo
- [ ] Definir variável `DATABASE_URL` no Railway
- [ ] Esperar deploy terminar (2-3 min)
- [ ] Copiar a **Public URL** do backend (vai usar no Vercel)
- [ ] Testar API: curl https://seu-backend-railway.app/api/presets/

## Vercel Setup (Frontend)
- [ ] Criar conta no Vercel (com GitHub)
- [ ] Importar repositório GitHub
- [ ] Definir Root Directory: frontend
- [ ] Definir Build Command: npm install && npm run build
- [ ] Definir Output Directory: dist
- [ ] Adicionar Environment Variable: REACT_APP_API_URL = URL do Railway
- [ ] Fazer deploy
- [ ] Esperar deploy terminar (2-3 min)
- [ ] Copiar a URL final do Vercel

## Testes
- [ ] Acessar frontend: https://seu-frontend.vercel.app
- [ ] Dashboard carrega corretamente
- [ ] Aba Presets mostra 10 presets
- [ ] Aba Casos carrega casos
- [ ] API retorna presets

## Configurações Finais
- [ ] Testar no MacBook (Safari)
- [ ] Testar no iPhone (Safari)
- [ ] Testar no Windows (Chrome/Edge)
- [ ] Verificar responsividade em celular
- [ ] Criar atalho no Home Screen (iPhone)
- [ ] Instalar como app (Android)

## Documentação
- [ ] Compartilhar URL com sua equipe
- [ ] Salvar URLs em lugar seguro
- [ ] Entender como fazer updates (git push)

---

Status: [ ] Tudo Pronto
