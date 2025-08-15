
package Internship_Tasks;


import java.util.*;
    

class Question {
    String question;
    String[] options;
    int correctAnswer; // index (1-4)

    public Question(String question, String[] options, int correctAnswer) {
        this.question = question;
        this.options = options;
        this.correctAnswer = correctAnswer;
    }
}

public class Task_8_Mini_Project_Online_Quiz_App {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);

        // Step 1: Create questions
        List<Question> questions = new ArrayList<Question>();
        questions.add(new Question(
                "Which language is used for Android development?",
                new String[]{"Java", "Python", "C#", "Ruby"}, 1));
        questions.add(new Question(
                "What does JDBC stand for?",
                new String[]{"Java DataBase Connectivity", "Java Design By Classes", "Joint DataBase Connection", "Java Development Basics"}, 1));
        questions.add(new Question(
                "Which company developed Java?",
                new String[]{"Microsoft", "Sun Microsystems", "Google", "Oracle"}, 2));
        questions.add(new Question(
                "What is the extension of Java bytecode files?",
                new String[]{".java", ".class", ".byte", ".exe"}, 2));
        questions.add(new Question(
                "Which keyword is used to inherit a class in Java?",
                new String[]{"implements", "extends", "inherits", "super"}, 2));

        int score = 0;

        // Step 2: Ask questions
        for (int i = 0; i < questions.size(); i++) {
            Question q = questions.get(i);
            System.out.println("\nQ" + (i + 1) + ". " + q.question);
            for (int j = 0; j < q.options.length; j++) {
                System.out.println((j + 1) + ". " + q.options[j]);
            }
            System.out.print("Your answer (1-4): ");
            int answer = sc.nextInt();

            if (answer == q.correctAnswer) {
                System.out.println("✅ Correct!");
                score++;
            } else {
                System.out.println("❌ Wrong! Correct answer: " + q.correctAnswer + ". " + q.options[q.correctAnswer - 1]);
            }
        }

        // Step 3: Show result
        System.out.println("\nQuiz Finished!");
        System.out.println("Your score: " + score + " / " + questions.size());

        if (score == questions.size()) {
            System.out.println("🏆 Excellent! Perfect score.");
        } else if (score >= questions.size() / 2) {
            System.out.println("👍 Good job! You passed.");
        } else {
            System.out.println("📚 Keep practicing!");
        }

        sc.close();
    }
}
