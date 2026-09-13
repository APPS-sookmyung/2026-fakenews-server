package com.fakenews.server.domain.post.dto;

import lombok.Data;

@Data
public class PostRegisterReqDto {
    private Long simulationId;

    private Long participantId;

    private String content;

    private Boolean isInitial;

    private Long userId;

    private Long simulationAgentId;
}
