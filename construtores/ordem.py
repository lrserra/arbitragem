class Ordem:
    def __init__(self):
       self.ativo_parte = ''
       self.ativo_contraparte = ''
       self.id = 0
       self.code = ''
       self.status = ''
       self.direcao = ''
       self.tipo_ordem = ''
       self.mensagem = ''
       self.preco_enviado = 0.0
       self.preco_executado = 0.0
       self.quantidade_enviada = 0.0
       self.quantidade_executada = 0.0
       self.foi_executada_completamente =False
       
