package org.example.backend.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

public class Transaction {

    @NotBlank
    private String transactionId;

    @NotBlank
    private String userId;

    @NotBlank
    private String accountId;

    @NotBlank
    private String timestamp;

    @NotNull
    @Positive
    private Double amount;

    @NotBlank
    private String transactionType; // CREDIT or DEBIT

    @NotBlank
    private String narration;

    @NotNull
    private Double balanceAfter;

    @NotBlank
    private String bankName;

    public Transaction() {}

    public String getTransactionId() { return transactionId; }
    public void setTransactionId(String transactionId) { this.transactionId = transactionId; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getAccountId() { return accountId; }
    public void setAccountId(String accountId) { this.accountId = accountId; }

    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }

    public Double getAmount() { return amount; }
    public void setAmount(Double amount) { this.amount = amount; }

    public String getTransactionType() { return transactionType; }
    public void setTransactionType(String transactionType) { this.transactionType = transactionType; }

    public String getNarration() { return narration; }
    public void setNarration(String narration) { this.narration = narration; }

    public Double getBalanceAfter() { return balanceAfter; }
    public void setBalanceAfter(Double balanceAfter) { this.balanceAfter = balanceAfter; }

    public String getBankName() { return bankName; }
    public void setBankName(String bankName) { this.bankName = bankName; }
}