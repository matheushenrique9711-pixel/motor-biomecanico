# Motor Biomecânico - Guia de Uso da Interface Web

## Visão Geral

A interface web do Motor Biomecânico foi completamente renovada para fornecer uma experiência intuitiva e visual para gerenciar seus casos clínicos e aplicar presets de condições de pé.

## Como Acessar

Após iniciar os serviços com docker-compose:

```bash
docker-compose up -d
```

A interface estará disponível em:
- **URL:** http://localhost:3000
- **API Backend:** http://localhost:8000/api

## Componentes Principais

### 1. Header (Cabeçalho)

Exibe o logo e título da aplicação com um gradiente visual que representa a qualidade clínica do sistema.

```
🦵 Motor Biomecânico
Sistema de Palmilhas Ortopédicas 3D Customizadas
```

### 2. Navigation Bar (Barra de Navegação)

Três abas principais para navegar entre seções:

- **ℹ️ Informações** - Visão geral do sistema
- **📋 Presets** - Biblioteca de condições de pé
- **📊 Casos** - Gerenciamento de casos clínicos

Cada aba mostra um contador com o número de itens.

### 3. Seção de Informações

Fornece um overview completo do sistema:

**Subseções:**
- Presets de Condições de Pé (10 presets disponíveis)
- Casos Clínicos (gestão de pacientes)
- Como Usar (guia passo a passo)
- Estatísticas (cards com números principais)

**Cards de Estatísticas:**
- Total de Presets Disponíveis
- Total de Casos Clínicos
- Total de Estados de Workflow (13 estados)

### 4. Seção de Presets

Exibe todos os 10 presets agrupados por severidade:

#### Organização por Severidade

```
🟢 Leve
  - Pé Cavo
  - Pé Plano Leve
  - Pé de Atleta

🟡 Moderada
  - Joanete
  - Metatarsalgia
  - Fascite Plantar
  - Dedos em Garra

🔴 Severa
  - Pé Plano Moderado
  - Pé Plano Severo

🟣 Máximo
  - Pé Diabético
```

#### Card de Preset

Cada preset exibe:

**Cabeçalho:**
- Nome da condição
- Badge de severidade (com cor)

**Corpo:**
- Descrição detalhada
- Informações técnicas:
  - Suporte de Arco
  - Altura de Calcanhar (mm)
  - Recomendação de Material

**Seção Clínica:**
- Indicadores Clínicos (lista de até 3)
- Queixas Comuns (lista de até 3)

**Interação:**
- Clique no card para selecioná-lo e ver detalhes completos
- O card selecionado é destacado com borda azul
- Efeito hover com sombra aumentada

### 5. Seção de Casos

Dividida em dois painéis:

#### Painel de Lista (esquerda)

Lista todos os casos clínicos com:
- ID do caso
- Status (com cor correspondente)
- Nome do paciente
- Data de criação

**Filtros implícitos:**
- Ordenados por data de criação (mais recentes primeiro)
- Scroll disponível se houver muitos casos

#### Painel de Detalhes (direita)

Quando um caso é selecionado, exibe:

**Informações do Caso:**
- ID do Caso
- Nome do Paciente
- Status (badge colorido)
- Condição Primária

**Aplicar Preset de Condição:**
Botões para aplicar qualquer um dos 10 presets:
- Clique em um botão para aplicar imediatamente
- Exibe confirmação de sucesso
- Os parâmetros são salvos no banco de dados
- O caso é recarregado com os novos parâmetros

## Cores e Significados

### Severidade

| Cor | Significado | Exemplos |
|-----|-------------|----------|
| 🟢 Verde | Leve | Pé Cavo, Pé Plano Leve |
| 🟡 Amarelo | Moderada | Fascite Plantar, Metatarsalgia |
| 🔴 Vermelho | Severa | Pé Plano Severo |
| 🟣 Roxo | Máximo | Pé Diabético |

### Status do Caso

| Status | Cor | Significado |
|--------|-----|------------|
| CREATED | Azul | Caso recém criado |
| ANALYZED | Verde | Análise biomecânica concluída |
| SUGGESTIONS_GENERATED | Roxo | Sugestões geradas |
| EXPORTED | Verde | Pronto para fabricação |

## Fluxo de Trabalho

### Cenário Típico: Novo Paciente com Pé Plano

1. **Acessar a Interface**
   - Abra http://localhost:3000

2. **Ver Presets Disponíveis**
   - Clique em "📋 Presets"
   - Procure "Pé Plano Leve" ou "Pé Plano Moderado"
   - Clique no card para ver detalhes completos

3. **Criar Novo Caso**
   - Use a API para criar um caso: `POST /api/cases/`
   - Ou use a página de casos

4. **Aplicar Preset**
   - Vá para "📊 Casos"
   - Selecione o novo caso
   - Clique no botão "Pé Plano Leve"
   - Confirmação: "Preset aplicado com sucesso"

5. **Parâmetros Aplicados**
   - A palmilha agora tem:
     - Suporte de Arco: Médio
     - Altura de Calcanhar: 12mm
     - Material: Poliuretano customizado
     - Contorno de Arco: Sim

6. **Próximos Passos**
   - Fazer análise biomecânica (POST /analyze)
   - Gerar sugestões de ajustes (POST /suggestions)
   - Gerar geometria 3D (POST /generate-geometry)
   - Exportar STL para impressão (POST /export-stl)

## Funcionalidades Avançadas

### Busca de Preset por Severidade

Via API:
```bash
curl http://localhost:8000/api/presets/severity/moderada
```

Retorna todos os presets da severidade "moderada".

### Atualizar Parâmetros Após Aplicar Preset

Após aplicar um preset, você pode:

1. **Via API:** fazer POST para `/cases/{case_id}/apply-adjustments` com parâmetros customizados
2. **Manualmente:** editar os valores na interface (quando disponível)

Os presets servem como ponto de partida, não como limite.

## Responsividade

A interface é completamente responsiva:

**Desktop (>1024px):**
- Layout 2 colunas na seção de casos
- Grid de presets 3+ colunas
- Navegação normal

**Tablet (768px-1024px):**
- Casos em layout de coluna única
- Grid de presets 2 colunas
- Navegação compacta

**Móvel (<768px):**
- Tudo em coluna única
- Presets em grid responsivo 1-2 colunas
- Navegação stackada

## Tratamento de Erros

A interface exibe mensagens claras:

**Erro (vermelho):**
```
❌ Erro ao carregar casos: [motivo]
```

**Sucesso (verde):**
```
✅ Preset "Pé Plano Leve" aplicado com sucesso ao caso CASE-123
```

As mensagens desaparecem automaticamente após 3 segundos.

## Performance

**Otimizações implementadas:**
- Componentes reutilizáveis
- Estados gerenciados eficientemente
- Requisições HTTP minimizadas
- Scroll virtual para listas longas (futura)
- Cache local de dados (futura)

**Tempo de carregamento esperado:**
- Primeira carga: < 2s
- Aplicar preset: < 1s
- Mudar de aba: < 0.5s

## Acessibilidade

**Recursos de acessibilidade:**
- Cores com contraste suficiente
- Sem dependência exclusiva de cor para significado
- Navegação completa por teclado
- Labels descritivos
- Estrutura semântica HTML

## Próximas Melhorias Planejadas

- [ ] Busca/filtro de casos e presets
- [ ] Edição inline de parâmetros
- [ ] Histórico de modificações
- [ ] Exportação de relatório em PDF
- [ ] Integração com câmera para captura de fotos
- [ ] Modo dark (tema escuro)
- [ ] Multi-idioma (português, inglês)
- [ ] Suporte a análise de vídeo de marcha

## Troubleshooting

### Interface não carrega

**Problema:** Página em branco ou erro de conexão

**Solução:**
```bash
# Verificar se backend está rodando
curl http://localhost:8000/api/health

# Verificar logs
docker-compose logs frontend
docker-compose logs backend
```

### Presets não aparecem

**Problema:** Lista vazia na aba de presets

**Solução:**
1. Aguarde inicialização completa (30-60 segundos)
2. Recarregue a página (F5)
3. Verifique os logs do backend:
```bash
docker-compose logs backend | grep -i preset
```

### Erro ao aplicar preset

**Problema:** Mensagem de erro ao clicar em "Aplicar Preset"

**Solução:**
1. Verifique se o caso existe
2. Verifique se o preset existe
3. Veja os logs de erro detalhados
4. Tente aplicar novamente

## Referência Rápida de URLs

| Página | URL |
|--------|-----|
| Dashboard Principal | http://localhost:3000 |
| API - Presets | http://localhost:8000/api/presets/ |
| API - Casos | http://localhost:8000/api/cases/ |
| API - Docs | http://localhost:8000/docs |
| Redoc | http://localhost:8000/redoc |
| Health Check | http://localhost:8000/api/health |

---

**Versão da Interface:** 1.0  
**Data:** 2026-09-28  
**Motor Biomecânico** - Sistema Integrado de Palmilhas Ortopédicas 3D
