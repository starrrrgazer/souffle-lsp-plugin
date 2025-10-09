package parsing;

import java.io.*;
import java.nio.file.*;
import java.util.*;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

public class BatchASTAnalyzer {

    public static void main(String[] args) {
        // 1️⃣ 获取项目根目录下的 gen_datasets 文件夹
        String projectRoot = System.getProperty("user.dir");
        String folderPath = Paths.get(projectRoot, "gen_datasets").toString();
        String outputFile = Paths.get(projectRoot, "ast_stats.xlsx").toString();

        List<Result> results = new ArrayList<>();

        System.out.println("📂 Analyzing folder: " + folderPath);

        try {
            Files.walk(Paths.get(folderPath))
                    .filter(Files::isRegularFile)
                    .filter(p -> p.toString().endsWith(".dl"))
                    .forEach(p -> {
                        try {
                            String absPath = p.toAbsolutePath().toString();
                            TreeStatsUtil.TreeStats stats = TreeStatsUtil.computeStatsFromFile(absPath);
                            results.add(new Result(absPath, stats.maxDegree, stats.maxDepth));
                            System.out.println("Success: " + absPath + " → " + stats);
                        } catch (Exception e) {
                            System.err.println("Failed on " + p + ": " + e.getMessage());
                        }
                    });

            writeToExcel(results, outputFile);
            System.out.println("\n All results written to: " + outputFile);

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    static class Result {
        String filePath;
        int maxDegree;
        int maxDepth;
        Result(String filePath, int maxDegree, int maxDepth) {
            this.filePath = filePath;
            this.maxDegree = maxDegree;
            this.maxDepth = maxDepth;
        }
    }

    private static void writeToExcel(List<Result> results, String outputFile) throws IOException {
        Workbook wb = new XSSFWorkbook();
        Sheet sheet = wb.createSheet("AST Stats");

        Row header = sheet.createRow(0);
        header.createCell(0).setCellValue("File (Absolute Path)");
        header.createCell(1).setCellValue("Max Degree");
        header.createCell(2).setCellValue("Max Depth");

        int rowNum = 1;
        for (Result r : results) {
            Row row = sheet.createRow(rowNum++);
            row.createCell(0).setCellValue(r.filePath);
            row.createCell(1).setCellValue(r.maxDegree);
            row.createCell(2).setCellValue(r.maxDepth);
        }

        for (int i = 0; i < 3; i++) sheet.autoSizeColumn(i);

        try (FileOutputStream fos = new FileOutputStream(outputFile)) {
            wb.write(fos);
        }
        wb.close();
    }
}
