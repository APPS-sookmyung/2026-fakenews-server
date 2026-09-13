package com.fakenews.server.domain.repost.entity;

import com.fakenews.server.domain.post.entity.Post;
import com.fakenews.server.domain.participant.entity.Participant;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;

import java.time.LocalDateTime;

@Entity
@Table(name = "repost")
@Getter
@NoArgsConstructor
public class Repost {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "repost_id")
    private Long repostId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "post_id")
    private Post post;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "participant_id")
    private Participant participant;

    @CreatedDate
    @Column(name = "created_at")
    private LocalDateTime createdAt;
}