from js_runtime import JavaScriptExecutionError, JavaScriptRuntime


def run_js(source: str) -> str:
    return JavaScriptRuntime().execute(source)


def test_odd_even():
    assert run_js(
        """
        let num = 7;
        if (num % 2 === 0) {
          console.log(num + " is Even");
        } else {
          console.log(num + " is Odd");
        }
        """
    ) == "7 is Odd"


def test_triangle():
    assert run_js(
        """
        for (let i = 1; i <= 5; i++) {
          let row = "";
          for (let j = 1; j <= i; j++) {
            row += "*";
          }
          console.log(row);
        }
        """
    ) == "*\n**\n***\n****\n*****"


def test_armstrong():
    assert run_js(
        """
        function isArmstrong(num) {
          let temp = num;
          let sum = 0;
          while (temp > 0) {
            let digit = temp % 10;
            sum += digit ** 3;
            temp = Math.floor(temp / 10);
          }
          return sum === num;
        }
        console.log(isArmstrong(153));
        console.log(isArmstrong(123));
        """
    ) == "true\nfalse"


def test_array_reverse():
    assert run_js(
        """
        let arr = [1, 2, 3, 4, 5];
        let reversed = [...arr].reverse();
        console.log("Original: " + arr.join(", "));
        console.log("Reversed: " + reversed.join(", "));
        """
    ) == "Original: 1, 2, 3, 4, 5\nReversed: 5, 4, 3, 2, 1"


def test_palindrome():
    assert run_js(
        """
        let str = "racecar";
        let reversed = str.split("").reverse().join("");
        if (str === reversed) {
          console.log(str + " is a Palindrome");
        } else {
          console.log(str + " is not a Palindrome");
        }
        """
    ) == "racecar is a Palindrome"


def test_hidden_style_features():
    assert run_js(
        """
        const nums = [1, 2, 3, 4, 5];
        const doubledEvens = nums.filter((n) => n % 2 === 0).map((n) => n * 2);
        function sum(...values) {
          return values.reduce((total, value) => total + value, 0);
        }
        console.log([...doubledEvens, 10].join("|"));
        console.log(sum(...doubledEvens));
        console.log(" racecar ".trim().slice(0, 4));
        """
    ) == "4|8|10\n12\nrace"


def test_errors_are_wrapped():
    try:
        run_js("const value = ;")
    except JavaScriptExecutionError as exc:
        assert "SyntaxError" in str(exc)
    else:
        raise AssertionError("Expected JavaScriptExecutionError")

def test_object_access():
    assert run_js(
        """
        let person = {
          name: "Anjali",
          age: 24
        };
        console.log(person.name);
        console.log(person.age);
        """
    ) == "Anjali\n24"


def test_array_methods():
    assert run_js(
        """
        let nums = [1, 2, 3, 4, 5];
        console.log(nums.includes(3));
        console.log(nums.indexOf(4));
        console.log(nums.slice(1, 4).join(","));
        """
    ) == "true\n3\n2,3,4"


def test_arrow_function():
    assert run_js(
        """
        const square = (x) => x * x;
        console.log(square(6));
        """
    ) == "36"


def test_string_methods():
    assert run_js(
        """
        let str = "  Hello JavaScript  ";
        console.log(str.trim());
        console.log(str.toUpperCase().includes("JAVA"));
        """
    ) == "Hello JavaScript\ntrue"


def test_spread_operator():
    assert run_js(
        """
        let arr1 = [1, 2];
        let arr2 = [...arr1, 3, 4];
        console.log(arr2.join(","));
        """
    ) == "1,2,3,4"