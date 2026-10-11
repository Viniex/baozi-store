package br.com.baozistore.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

/** Corpo do POST/PUT /pedidos: { "clienteId": 1, "produtoId": 1, "quantidade": 5 } */
public record PedidoRequest(
        @NotNull(message = "clienteId é obrigatório") Long clienteId,
        @NotNull(message = "produtoId é obrigatório") Long produtoId,
        @NotNull(message = "quantidade é obrigatória")
        @Min(value = 1, message = "quantidade deve ser no mínimo 1") Integer quantidade
) {
}
