using Shop;

public class PriceCalculatorTests
{
    private static Order OrderOf(CustomerType customer) =>
        new(customer, [new OrderLine("A", 100m, 2), new OrderLine("B", 50m, 1)]);

    [Fact]
    public void Regular_customer_pays_the_subtotal() =>
        Assert.Equal(250m, PriceCalculator.Total(OrderOf(CustomerType.Regular)));

    [Fact]
    public void Loyal_customer_gets_five_percent_off() =>
        Assert.Equal(237.50m, PriceCalculator.Total(OrderOf(CustomerType.Loyal)));
}
