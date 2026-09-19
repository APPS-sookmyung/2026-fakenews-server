package com.fakenews.server.domain.post.entity;

import jakarta.persistence.*;
import lombok.Getter;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

@Getter
@Entity
public class Post {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long postId;

    private Long simulationId;

    private Long participantId;
    
    private Long originalPostId;

    @Column(nullable = false, length = 10000)
    private String content;

    private Boolean isInitial;

    @CreationTimestamp
    @Column(name = "created_at",updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "deleted")
    private Boolean deleted;

    private Long userId;

    private Long simulationAgentId;

    public static Post create(String content, Long userId) {
        Post post = new Post();
        post.content = content;
        post.userId = userId;
        post.isInitial = false;
        post.deleted = false;
        return post;
    }
}
