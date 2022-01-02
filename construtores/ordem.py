class Ordem:
    def __init__(self,ativo_parte='',quantidade_enviada=0,preco_enviado=0,tipo_ordem=''):
       self.ativo_parte = ativo_parte
       self.ativo_contraparte = ''
       self.id = 0
       self.code = ''
       self.status = ''
       self.direcao = ''
       self.tipo_ordem = tipo_ordem
       self.mensagem = ''
       self.preco_enviado = preco_enviado
       self.preco_executado = 0.0
       self.quantidade_enviada = quantidade_enviada
       self.quantidade_executada = 0.0
       self.foi_executada_completamente =False
       
