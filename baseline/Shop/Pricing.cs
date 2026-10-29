namespace Shop;

public enum CustomerType { Regular, Loyal }

public record OrderLine(string Sku, decimal UnitPrice, int Quantity);

public record Order(CustomerType Customer, IReadOnlyList<OrderLine> Lines);

public static class PriceCalculator
{
    public static decimal Total(Order order)
    {
        var subtotal = order.Lines.Sum(l => l.UnitPrice * l.Quantity);
        var discount = order.Customer switch
        {
            CustomerType.Loyal => subtotal * 0.05m,
            _ => 0m
        };
        return subtotal - discount;
    }
}
