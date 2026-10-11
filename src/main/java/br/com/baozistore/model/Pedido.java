package br.com.baozistore.model;

import jakarta.persistence.*;

/**
 * Pedido simples: um cliente compra UM produto em determinada quantidade.
 * No banco, as colunas cliente_id e produto_id são chaves estrangeiras (conforme o DER).
 */
@Entity
@Table(name = "pedido")
public class Pedido {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER, optional = false)
    @JoinColumn(name = "cliente_id", nullable = false)
    private Cliente cliente;

    @ManyToOne(fetch = FetchType.EAGER, optional = false)
    @JoinColumn(name = "produto_id", nullable = false)
    private Produto produto;

    @Column(nullable = false)
    private Integer quantidade;

    public Pedido() {
    }

    public Pedido(Cliente cliente, Produto produto, Integer quantidade) {
        this.cliente = cliente;
        this.produto = produto;
        this.quantidade = quantidade;
    }

    /** Exposto no JSON como "clienteId" (atributo sugerido no enunciado). */
    @Transient
    public Long getClienteId() {
        return cliente != null ? cliente.getId() : null;
    }

    /** Exposto no JSON como "produtoId" (atributo sugerido no enunciado). */
    @Transient
    public Long getProdutoId() {
        return produto != null ? produto.getId() : null;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Cliente getCliente() { return cliente; }
    public void setCliente(Cliente cliente) { this.cliente = cliente; }

    public Produto getProduto() { return produto; }
    public void setProduto(Produto produto) { this.produto = produto; }

    public Integer getQuantidade() { return quantidade; }
    public void setQuantidade(Integer quantidade) { this.quantidade = quantidade; }
}
