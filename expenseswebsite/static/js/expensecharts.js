const ctx1 = document.getElementById("myChart1").getContext("2d");
const ctx2 = document.getElementById("myChart2").getContext("2d");

const getRandomType = () => {
  const types = [
    "bar",
    "horizontalBar",
    "pie",
    "line",
    "radar",
    "doughnut",
    "polarArea",
  ];
  return types[Math.floor(Math.random() * types.length)];
};

const displayChart1 = (data, labels) => {
  const type = 'doughnut';
  const myChart = new Chart(ctx1, {
    type: type,
    data: {
      labels: labels,
      datasets: [
        {
          label: `Amount (Last 6 months) (${type} View)`,
          data: data,
          backgroundColor: [
            "rgba(255, 99, 132, 0.2)",
            "rgba(54, 162, 235, 0.2)",
            "rgba(255, 99, 132,0.7)",
            "rgba(75, 192, 192, 0.2)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 99, 132,0.7)",
            "rgba(75, 192, 192, 1)",
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      title: {
        display: true,
        text: "Expense Distribution Per Category",
        fontSize: 25,
      },
      legend: {
        display: true,
        position: "right",
        labels: {
          fontColor: "#000",
        },
      },
    },
  });
};
const displayChart2 = (data, labels) => {
  const type = 'line';
  const myChart = new Chart(ctx2, {
    type: type,
    data: {
      labels: labels,
      datasets: [
        {
          label: `Amount (Last 6 months) (${type} View)`,
          data: data,
          backgroundColor: [
            "rgba(255, 99, 132, 0.2)",
            "rgba(54, 162, 235, 0.2)",
            "rgba(255, 99, 132,0.7)",
            "rgba(75, 192, 192, 0.2)",
          ],
          borderColor: [
            "rgba(255, 99, 132, 1)",
            "rgba(54, 162, 235, 1)",
            "rgba(255, 99, 132,0.7)",
            "rgba(75, 192, 192, 1)",
          ],
          borderWidth: 1,
        },
      ],
    },
    options: {
      title: {
        display: true,
        text: "Expense Distribution Per Category",
        fontSize: 25,
      },
      legend: {
        display: true,
        position: "right",
        labels: {
          fontColor: "#000",
        },
      },
    },
  });
};

const getCategoryData = () => {
  fetch("/expense_category_summary")
    .then((res) => res.json())
    .then((res1) => {
      if (res1 && res1.expenses_category_data) {
        const results = res1.expenses_category_data;
        const labels = Object.keys(results);
        const data = Object.values(results);
        displayChart1(data, labels);
        displayChart2(data, labels);
      } else {
        console.error("Invalid data format:", res1);
      }
    })
    .catch((error) => console.error("Error fetching data:", error));
};

window.onload = getCategoryData;
