import math
import unittest
from unittest.mock import mock_open,patch

from main import (
    parse_arguments,
    read_toml_file,
    parse_global_const,
    evaluate_expression,
    validate_name,
    tranform_value,
    transfotm_toml,
    write_output
)

class test_parser(unittest.TestCase):
    
    def test_parse_arguments(self) -> None:
        test_args = [
        "--input_file", "input_file.toml",
        "--output_file", "output_file.txt"
        ]
        result_args = parse_arguments(test_args)
        self.assertEqual(result_args.input_file, "input_file.toml")
        self.assertEqual(result_args.output_file, "output_file.txt")
        print('\n---\nparser is working\n---')
        
        
    def test_read_toml_file(self):
        test_file_path = "test_input_file.toml"
        test_result = read_toml_file(test_file_path)
        self.assertEqual(test_result,
                         {'a': 1, 'b': 3, 'c': 'aboba'})
        print('\n---\nreader is working\n---')

    def test_parse_global_const(self):
        test_line = 'global server_name = "example_server"'
        constants = parse_global_const(test_line)
        print('\n',constants)
        print('---\nglobals has been parsed\n---')
        
    
    def test_evaluate_expression(self):
        def evaluate_expression(expr):
            expr = expr.strip()
            for name, value in constants.items():
                expr = expr.replace(name, str(value))
            
            allowed_globals = {"max": max, "pow": pow, "math": math}
            try:
                return eval(expr, {"__builtins__":None}, allowed_globals)
            except Exception as e:
                raise ValueError(f"Ошибка вычисления выражения '{expr}': {e}")
        
        constants = {}
        constants["pi"] = 3.14
        self.assertEqual(evaluate_expression("2 * pi"), 6.28)
        self.assertEqual(evaluate_expression("pow(2, 3)"), 8)
        self.assertRaises(ValueError, evaluate_expression, "2 / 0")
        print('\n---\nexpression has been evaluated\n---')

    def test_validate_name(self):
        self.assertIsNone(validate_name("valid_name"))
        with self.assertRaises(ValueError):
            validate_name("invalid-name")  # Некорректное имя с дефисом
        with self.assertRaises(ValueError):
            validate_name("123invalid")  # Начинается с числа
        print('\n---\nname has been validated\n---')

    
    def test_tranform_value(self):
        self.assertEqual(tranform_value(42), "42")
        self.assertEqual(tranform_value("Hello"), '"Hello"')
        self.assertEqual(tranform_value([1, 2, 3]), "<< 1, 2, 3 >>")
        self.assertEqual(tranform_value({"key": "value"}), "[\n   key => \"value\"\n]")
        self.assertRaises(ValueError, tranform_value, set([1, 2, 3]))
        print('\n---\ntranform_value is working\n---')

    def test_transfotm_toml(self):
        data = {
            "valid_name": "some_value",
            "another_valid_name": [1, 2, 3],
        }
        result = transfotm_toml(data)
        self.assertIn('valid_name = "some_value"', result)
        self.assertIn("another_valid_name = << 1, 2, 3 >>", result)
        self.assertRaises(ValueError, transfotm_toml, {"invalid-name": "value"})
        print('\n---\ntransfotm_toml is working\n---')

    @patch("builtins.open", new_callable=mock_open)
    def test_write_output(self, mock_file):
        write_output("output.txt", "some data")
        mock_file.assert_called_once_with("output.txt", "w")
        mock_file().write.assert_called_once_with("some data")
    
if __name__ == "__main__":
    unittest.main()