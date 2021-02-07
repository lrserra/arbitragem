class Ordem:
    def __init__(self):
       self.ativo = ''
       self.id = 0
       self.code = ''
       self.preco_compra = 0.0
       self.preco_venda = 0.0
       self.preco_executado = 0.0
       self.quantidade_compra = 0.0
       self.quantidade_venda = 0.0
       self.quantidade_transferencia = 0.0
       self.quantidade_negociada = 0.0
       self.quantidade_executada = 0.0
       self.status = ''
       self.tipo_ordem = ''
       self.mensagem = ''
       self.descricao_status_executado ='filled'