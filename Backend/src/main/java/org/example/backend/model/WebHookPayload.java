package org.example.backend.model;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import java.util.List;

public class WebHookPayload {

    @NotBlank
    private String consentId;

    @NotBlank
    private String userId;

    @NotBlank
    private String fetchTimestamp;

    @NotBlank
    private String bankName;

    @NotNull
    @NotEmpty
    @Valid
    private List<Transaction> transactions;

    public WebHookPayload() {}

    public String getConsentId() { return consentId; }
    public void setConsentId(String consentId) { this.consentId = consentId; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getFetchTimestamp() { return fetchTimestamp; }
    public void setFetchTimestamp(String fetchTimestamp) { this.fetchTimestamp = fetchTimestamp; }

    public String getBankName() { return bankName; }
    public void setBankName(String bankName) { this.bankName = bankName; }

    public List<Transaction> getTransactions() { return transactions; }
    public void setTransactions(List<Transaction> transactions) { this.transactions = transactions; }
}