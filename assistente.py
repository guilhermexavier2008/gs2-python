"""Classe Assistente: atende o cidadão, guarda o histórico e calcula os indicadores."""

import csv
import json
import os
import time
from datetime import datetime

from orientacao import AVISO

CAMPOS_CSV = ["data", "sessao", "origem", "pergunta", "id_orientacao",
              "encontrou", "ajudou", "tentativas", "tempo", "nota"]


class Assistente:
    """Quem conversa com o cidadão. Tem uma BaseConhecimento (composição)."""

    def __init__(self, nome, base, caminho_historico="data/historico.json",
                 caminho_csv="data/atendimentos.csv"):
        self.nome = nome
        self.base = base
        self.caminho_historico = caminho_historico
        self.caminho_csv = caminho_csv
        self.sessao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.historico = self.carregar_historico()

    # ------------------------------------------------------------ entrada segura
    def ler_texto(self, mensagem):
        return input(mensagem).strip()

    def ler_opcao(self, mensagem, minimo, maximo):
        """Repete até o usuário digitar um número válido na faixa."""
        while True:
            texto = self.ler_texto(mensagem)
            if texto.isdigit() and minimo <= int(texto) <= maximo:
                return int(texto)
            print(f"Opção inválida. Digite um número de {minimo} a {maximo}.")

    def ler_sn(self, mensagem):
        """Repete até o usuário digitar s ou n."""
        while True:
            texto = self.ler_texto(mensagem).lower()
            if texto in ("s", "sim"):
                return "s"
            if texto in ("n", "nao", "não"):
                return "n"
            print("Resposta inválida. Digite apenas s ou n.")

    @staticmethod
    def tem_dado_pessoal(texto):
        """8 ou mais dígitos ou presença de @ indicam CPF, telefone ou e-mail."""
        digitos = sum(1 for letra in texto if letra.isdigit())
        return "@" in texto or digitos >= 8

    # ------------------------------------------------------------ histórico
    def carregar_historico(self):
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                return [item for item in dados if isinstance(item, dict)]
            print("Aviso: histórico em formato inesperado. Começando um novo.")
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            print("Aviso: histórico corrompido. Guardei uma cópia e comecei um novo.")
            try:
                os.replace(self.caminho_historico, self.caminho_historico + ".corrompido")
            except OSError:
                pass
        except OSError as erro:
            print(f"Aviso: não foi possível ler o histórico ({erro}).")
        return []

    def salvar_historico(self):
        try:
            pasta = os.path.dirname(self.caminho_historico)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError as erro:
            print(f"Aviso: não foi possível salvar o histórico ({erro}).")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou, tentativas, tempo):
        """Guarda um atendimento. Perguntas com dado pessoal nunca são registradas."""
        if self.tem_dado_pessoal(pergunta):
            return None
        atendimento = {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sessao": self.sessao,
            "origem": origem,
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo": tempo,
            "nota": None,
        }
        self.historico.append(atendimento)
        self.salvar_historico()
        return atendimento

    # ------------------------------------------------------------ atendimento
    def perguntar(self):
        """Busca por texto livre. Cada atendimento termina quando a pessoa diz que foi ajudada."""
        while self._atender_pergunta():
            pass

    def _atender_pergunta(self):
        """Um atendimento. Devolve True para continuar perguntando, False para voltar."""
        inicio = time.time()
        tentativas = 0
        ultima = None  # (texto, id da orientação, encontrou)
        while True:
            texto = self.ler_texto("\nDigite sua dúvida (0 para voltar): ")
            if texto == "0":
                if ultima is not None:
                    self.registrar("pergunta", ultima[0], ultima[1], ultima[2], False,
                                   tentativas, round(time.time() - inicio, 1))
                return False
            if texto == "":
                print("Você não digitou nada. Escreva sua dúvida ou digite 0 para voltar.")
                continue
            if self.tem_dado_pessoal(texto):
                print("Atenção: não digite CPF, telefone ou e-mail. Reescreva.")
                continue

            tentativas += 1
            resultados = self.base.buscar(texto)
            if not resultados or self.base.confianca(resultados[0][0]) is None:
                print("\nNão encontrei uma orientação para essa dúvida.")
                print("Tente outras palavras (por exemplo, o nome do documento) "
                      "ou use a navegação por categorias:")
                print("  " + " | ".join(self.base.categorias()))
                ultima = (texto, None, False)
                continue

            pontos, melhor = resultados[0]
            print(f"\nConfiança da resposta: {self.base.confianca(pontos)} ({pontos} pontos)\n")
            melhor.exibir()
            alternativas = [o for p, o in resultados[1:3] if self.base.confianca(p)]
            if alternativas:
                print("\nOutras orientações que podem ajudar:")
                for alternativa in alternativas:
                    print(f"  - {alternativa.titulo}")

            if self.ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): ") == "s":
                self.registrar("pergunta", texto, melhor.id, True, True,
                               tentativas, round(time.time() - inicio, 1))
                return True
            ultima = (texto, melhor.id, True)
            print("Tente descrever de outro jeito ou use a navegação por categorias.")

    def navegar(self):
        """Navegação por categorias, com 0 para voltar em todas as telas."""
        categorias = self.base.categorias()
        while True:
            print("\nCategorias:")
            for numero, categoria in enumerate(categorias, 1):
                print(f"  {numero}. {categoria}")
            print("  0. Voltar")
            opcao = self.ler_opcao("Escolha uma categoria: ", 0, len(categorias))
            if opcao == 0:
                return
            self._navegar_categoria(categorias[opcao - 1])

    def _navegar_categoria(self, categoria):
        orientacoes = self.base.por_categoria(categoria)
        while True:
            print(f"\n[{categoria}]")
            for numero, orientacao in enumerate(orientacoes, 1):
                print(f"  {numero}. {orientacao.titulo}")
            print("  0. Voltar")
            opcao = self.ler_opcao("Escolha uma orientação: ", 0, len(orientacoes))
            if opcao == 0:
                return
            inicio = time.time()
            orientacao = orientacoes[opcao - 1]
            print()
            orientacao.exibir()
            ajudou = self.ler_sn("\nEssa orientação respondeu sua dúvida? (s/n): ") == "s"
            self.registrar("categoria", orientacao.titulo, orientacao.id, True, ajudou,
                           1, round(time.time() - inicio, 1))

    # ------------------------------------------------------------ indicadores e CSV
    def indicadores(self):
        """Calcula e exibe os indicadores. Devolve um dicionário com os valores."""
        total = len(self.historico)
        if total == 0:
            print("\nAinda não há atendimentos registrados.")
            return None

        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudados = [a for a in self.historico if a.get("ajudou")]
        tempos = [a.get("tempo", 0) for a in ajudados]
        tentativas = [a.get("tentativas", 1) for a in self.historico]
        notas = {a["sessao"]: a["nota"] for a in self.historico
                 if a.get("nota") is not None and "sessao" in a}
        sem_solucao = []
        for a in self.historico:
            if a.get("origem") == "pergunta" and not a.get("ajudou") and a.get("pergunta"):
                if a["pergunta"] not in sem_solucao:
                    sem_solucao.append(a["pergunta"])

        resultado = {
            "atendimentos": total,
            "encontrada_pct": round(100 * len(encontrados) / total, 1),
            "acerto_pct": round(100 * len(ajudados) / total, 1),
            "tempo_medio": round(sum(tempos) / len(tempos), 1) if tempos else None,
            "tentativas_medias": round(sum(tentativas) / total, 1),
            "facilidade": round(sum(notas.values()) / len(notas), 1) if notas else None,
            "sem_solucao": sem_solucao,
        }

        tempo_txt = f"{resultado['tempo_medio']} s" if tempos else "-"
        facilidade_txt = f"{resultado['facilidade']}" if notas else "-"
        print(f"\n=== Indicadores ({total} atendimentos) ===")
        print(f"Resposta encontrada (%): {resultado['encontrada_pct']}")
        print(f"Taxa de acerto: ajudou (%): {resultado['acerto_pct']}")
        print(f"Tempo médio para encontrar: {tempo_txt}")
        print(f"Tentativas por atendimento: {resultado['tentativas_medias']}")
        print(f"Facilidade de uso (1 a 5): {facilidade_txt}")
        print("Dúvidas sem solução:")
        if sem_solucao:
            for duvida in sem_solucao:
                print(f"  - {duvida}")
        else:
            print("  (nenhuma)")
        return resultado

    def exportar_csv(self):
        """Exporta os atendimentos para CSV com csv.DictWriter."""
        try:
            pasta = os.path.dirname(self.caminho_csv)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_csv, "w", newline="", encoding="utf-8") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV, extrasaction="ignore")
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow(atendimento)
            print(f"\n{len(self.historico)} atendimento(s) exportado(s) para {self.caminho_csv}")
            return True
        except OSError as erro:
            print(f"\nNão foi possível exportar o CSV ({erro}). Feche o arquivo se ele estiver aberto.")
            return False

    # ------------------------------------------------------------ menu
    def finalizar(self):
        """Ao sair: pede a nota de facilidade, salva, exporta e mostra os indicadores."""
        da_sessao = [a for a in self.historico if a.get("sessao") == self.sessao]
        if da_sessao:
            nota = self.ler_opcao("\nDe 1 a 5, qual a facilidade de usar este assistente? ", 1, 5)
            for atendimento in da_sessao:
                atendimento["nota"] = nota
            self.salvar_historico()
        self.exportar_csv()
        self.indicadores()
        print("\nObrigado por usar o assistente!")

    def menu(self):
        print(f"\n===== {self.nome} =====")
        print("Orientações para jovens no primeiro emprego, com base em fontes oficiais.")
        print("Não pedimos nome, CPF, telefone nem e-mail.")
        print(AVISO)
        while True:
            print("\nMenu principal")
            print("  1. Fazer uma pergunta")
            print("  2. Navegar por categorias")
            print("  3. Ver indicadores")
            print("  4. Exportar atendimentos para CSV")
            print("  0. Sair")
            opcao = self.ler_opcao("Escolha uma opção: ", 0, 4)
            if opcao in (1, 2) and not self.base.orientacoes:
                print("A base de conhecimento está vazia ou não foi carregada. Verifique data/base_conhecimento.json.")
            elif opcao == 1:
                self.perguntar()
            elif opcao == 2:
                self.navegar()
            elif opcao == 3:
                self.indicadores()
            elif opcao == 4:
                self.exportar_csv()
            else:
                self.finalizar()
                return
