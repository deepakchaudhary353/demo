// AstExtractor/Program.cs
using System;
using System.Collections.Generic;
using System.IO; // Added to read files
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using System.Text.Json;

class AstExtractor
{
    static void Main(string[] args)
    {
        if (args.Length == 0) return;

        string filePath = args[0];
        string code = File.ReadAllText(filePath); // Read file content here

        SyntaxTree tree = CSharpSyntaxTree.ParseText(code);
        SyntaxNode root = tree.GetRoot();
        
        // Pass "CSharp" context to the root
        var ast = ConvertNode(root);

        var json = JsonSerializer.Serialize(ast, new JsonSerializerOptions { WriteIndented = true });
        Console.WriteLine(json);
    }

    static Dictionary<string, object> ConvertNode(SyntaxNode node)
    {
        var result = new Dictionary<string, object>
        {
            ["kind"] = node.Kind().ToString(), // This distinguishes the context (e.g., Method vs Class)
            ["text"] = node.ToString(),
            ["span"] = node.Span.ToString(), // Helps locate it in the file
            ["children"] = new List<Dictionary<string, object>>()
        };

        foreach (var child in node.ChildNodes())
        {
            ((List<Dictionary<string, object>>)result["children"]).Add(ConvertNode(child));
        }

        return result;
    }
}