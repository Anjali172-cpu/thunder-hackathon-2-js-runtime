const nums = [1, 2, 3, 4, 5];
const doubledEvens = nums
  .filter((value) => value % 2 === 0)
  .map((value) => value * 2);

function sum(...values) {
  return values.reduce((total, value) => total + value, 0);
}

const user = { name: "Ada", scores: [...doubledEvens, 10] };

switch (user.name) {
  case "Ada":
    console.log(user.name + ": " + sum(...user.scores));
    break;
  default:
    console.log("Unknown");
}

console.log("hello thunder".replace("thunder", "runtime").toUpperCase());
