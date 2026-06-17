import { useEffect, useState } from "react";
import "./App.css";

export default function App() {
  const [stocks, setStocks] = useState([]);

  useEffect(() => {
    fetch("https://cbvbq2ei92.execute-api.us-west-2.amazonaws.com/prod/movers")
      .then((res) => res.json())
      .then(setStocks)
      .catch(console.error);
  }, []);

  return (
    <div>
      <h1>Stock Movers</h1>

      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Ticker</th>
            <th>% Change</th>
          </tr>
        </thead>

        <tbody>
          {stocks.map((stock, i) => (
            <tr
              key={i}
              className={
                Number(stock.percent_change) >= 0 ? "green" : "red"
              }
            >
              <td>{stock.date}</td>
              <td>{stock.ticker_symbol}</td>
              <td>{Number(stock.percent_change).toFixed(2)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}