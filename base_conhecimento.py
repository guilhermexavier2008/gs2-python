"""Classe BaseConhecimento: lê o JSON, lista categorias e busca a melhor orientação."""

import json

from orientacao import Orientacao

ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ç": "c"}

# Palavras muito comuns que não devem render ponto no título (ajuste explicado no README).
STOPWORDS = {"como", "para", "onde", "fazer", "quero", "preciso", "posso",
             "qual", "quais", "quando", "sobre", "minha", "pelo", "pela"}

CAMPOS = ["id", "categoria", "titulo", "palavras_chave", "resposta",
          "documentos", "onde", "fonte", "verificado_em"]


def normalizar(texto):
    """Minúsculas, sem acentos e sem pontuação. Devolve o texto com espaço nas pontas."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in "?!.,;:()-/\"'":
        texto = texto.replace(sinal, " ")
    return " " + " ".join(texto.split()) + " "


class BaseConhecimento:
    """O conjunto de todas as orientações."""

    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Nunca trava: devolve False se falhar."""
        self.orientacoes = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            print(f"Aviso: base de conhecimento não encontrada em '{self.caminho}'.")
            return False
        except json.JSONDecodeError:
            print(f"Aviso: o arquivo '{self.caminho}' está corrompido (JSON inválido).")
            return False
        except OSError as erro:
            print(f"Aviso: não foi possível abrir a base de conhecimento ({erro}).")
            return False

        if not isinstance(dados, list):
            print("Aviso: a base de conhecimento deve ser uma lista de orientações.")
            return False

        ignoradas = 0
        for item in dados:
            if self._registro_valido(item):
                self.orientacoes.append(Orientacao(**{campo: item[campo] for campo in CAMPOS}))
            else:
                ignoradas += 1
        if ignoradas:
            print(f"Aviso: {ignoradas} registro(s) incompleto(s) foram ignorados.")
        return len(self.orientacoes) > 0

    @staticmethod
    def _registro_valido(item):
        if not isinstance(item, dict) or any(campo not in item for campo in CAMPOS):
            return False
        if not isinstance(item["id"], int):
            return False
        for campo in ("categoria", "titulo", "resposta", "onde", "fonte", "verificado_em"):
            if not isinstance(item[campo], str) or not item[campo].strip():
                return False
        for campo in ("palavras_chave", "documentos"):
            if not isinstance(item[campo], list) or not all(isinstance(x, str) for x in item[campo]):
                return False
        return len(item["palavras_chave"]) > 0

    def categorias(self):
        """Lista de categorias sem repetição, na ordem em que aparecem."""
        return list(dict.fromkeys(o.categoria for o in self.orientacoes))

    def por_categoria(self, categoria):
        """Orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        """+3 por palavra-chave presente na pergunta; +1 por palavra (4+ letras) no título."""
        texto = normalizar(pergunta)
        pontos = 0
        for chave in orientacao.palavras_chave:
            chave_norm = normalizar(chave)
            if chave_norm.strip() and chave_norm in texto:
                pontos += 3
        titulo = normalizar(orientacao.titulo)
        for palavra in set(texto.split()):
            if len(palavra) >= 4 and palavra not in STOPWORDS and f" {palavra} " in titulo:
                pontos += 1
        return pontos

    def buscar(self, pergunta):
        """Lista de tuplas (pontos, orientacao), da maior para a menor pontuação."""
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda par: (-par[0], par[1].id))
        return resultados

    @staticmethod
    def confianca(pontos):
        """ALTA (6+), MÉDIA (3 a 5) ou None (menos de 3 = não encontrei)."""
        if pontos >= 6:
            return "ALTA"
        if pontos >= 3:
            return "MÉDIA"
        return None
