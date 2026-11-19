# Citizen Assist AI

Repositório: https://github.com/guilhermexavier2008/gs2-python

Assistente de terminal em Python que orienta **jovens no primeiro emprego** com base em informações de fontes oficiais, mostrando a fonte, a data de verificação e um aviso de limitação, sem coletar dados pessoais.

> GS2026.2 – Pensamento Computacional e Automação com Python (FIAP)

## Integrantes

| Nome | RM |
|------|----|
| Guilherme Xavier | 573053 |
| Beckman Lugli | 573442 |
| Bryan Lugli | 571350 |

## Público e problema

**Público:** jovens que estão começando a trabalhar.
**Problema:** quem vai ao primeiro emprego precisa de CPF, conta gov.br, Carteira de Trabalho Digital, título de eleitor e conta para receber salário, e ainda precisa se proteger de golpes de falsa vaga. A informação existe, mas está espalhada e misturada com sites que parecem oficiais e não são.

## ODS relacionados

- **ODS 8** – Trabalho decente e crescimento econômico
- **ODS 10** – Redução das desigualdades (acesso à informação)
- **ODS 16** – Paz, justiça e instituições eficazes (acesso à informação e proteção contra golpes)

## Como executar

Requisitos: Python 3.8 ou superior. Não usa bibliotecas externas.

```
python main.py
```

O programa funciona de qualquer pasta. A base fica em `data/base_conhecimento.json`; o histórico em `data/historico.json`; o CSV é gerado em `data/atendimentos.csv` (ao sair ou na opção 4 do menu).

## Estrutura

```
citizen-assist-ai/
├── main.py              # inicia o programa
├── orientacao.py        # classe Orientacao
├── base_conhecimento.py # classe BaseConhecimento (+ normalizar)
├── assistente.py        # classe Assistente
└── data/
    ├── base_conhecimento.json
    ├── historico.json
    └── atendimentos.csv
```

Composição: `Assistente` → `base: BaseConhecimento` → `orientacoes: [Orientacao, ...]`.

## Regra de pontuação

A pergunta e os textos da base são normalizados (minúsculas, sem acentos, sem pontuação) e a pergunta é comparada com cada orientação:

| Regra | Pontos |
|-------|--------|
| Palavra-chave da orientação aparece na pergunta | +3 |
| Palavra da pergunta com 4+ letras aparece no título | +1 |

| Melhor pontuação | Resultado |
|------------------|-----------|
| 6 ou mais | Confiança ALTA |
| 3 a 5 | Confiança MÉDIA |
| menos de 3 | "Não encontrei": sugere outras palavras e as categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)` da maior para a menor pontuação. O assistente mostra a melhor orientação e até duas alternativas.

**Ajustes feitos nas regras (permitidos pelo enunciado):**

1. Palavras muito comuns ("como", "para", "onde", "fazer", etc.) não valem ponto no título, para não aproximar orientações que não têm relação.
2. Cada palavra da pergunta vale no máximo 1 ponto (não repete).
3. Alternativas só aparecem se também tiverem 3 pontos ou mais.
4. A normalização também troca `-` e `/` por espaço (para casar "gov.br" e "conta-salário").

## Regras de atendimento

- Navegação por categorias com "0 para voltar" em todas as telas.
- Entradas inválidas (letras, vazio, fora da faixa, s/n inválido) nunca encerram o programa.
- Pergunta com 8 ou mais dígitos ou com `@` é recusada e **não é registrada**.
- Toda resposta mostra fonte, data de verificação e o aviso de que não é canal oficial.
- JSON ausente ou corrompido não trava o programa (o histórico corrompido é guardado como `.corrompido`).

## Integração com outras disciplinas

Nenhuma integração com outras disciplinas nesta entrega.

## Fontes consultadas

- https://www.gov.br/governodigital
- https://www.gov.br/receitafederal
- https://www.poupatempo.sp.gov.br
- https://www.gov.br/trabalho-e-emprego
- https://www.tse.jus.br
- https://www.gov.br/defesa
- https://www.bcb.gov.br
- https://www.caixa.gov.br
- https://www.delegaciaeletronica.policiacivil.sp.gov.br
- https://www.gov.br/saude

## Resultado do teste com usuários

(Preencher depois de testar com pelo menos 3 pessoas de fora da equipe, somando 10 atendimentos ou mais. Não registrar nomes nem dados pessoais.)

| Indicador | Resultado |
|-----------|-----------|
| Resposta encontrada (%) | |
| Taxa de acerto: ajudou (%) | |
| Tempo médio para encontrar | |
| Tentativas por atendimento | |
| Facilidade de uso (1 a 5) | |

**Dúvidas sem solução:** (listar)

**Melhoria feita a partir do teste:** (ex.: nova palavra-chave para a dúvida X)

## Limitações

- A busca é por regras: só entende palavras-chave que estão na base, sem entender sinônimos ou erros de digitação.
- A base tem 14 orientações e precisa ser revisada periodicamente, pois regras e sites oficiais mudam.
- Alguns endereços são de São Paulo (Poupatempo, Delegacia Eletrônica); em outros estados os locais são diferentes.
- O assistente não é canal oficial e não substitui o atendimento do órgão responsável.

## Vídeo técnico

(colar o link do YouTube, não listado)
