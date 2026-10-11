package br.com.baozistore.repository;

import br.com.baozistore.model.Pedido;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

@Repository
public interface PedidoRepository extends JpaRepository<Pedido, Long> {

    @Query("select count(p) > 0 from Pedido p where p.cliente.id = :clienteId")
    boolean existsByClienteId(@Param("clienteId") Long clienteId);

    @Query("select count(p) > 0 from Pedido p where p.produto.id = :produtoId")
    boolean existsByProdutoId(@Param("produtoId") Long produtoId);
}
