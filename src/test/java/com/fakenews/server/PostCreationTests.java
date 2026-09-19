package com.fakenews.server;

import com.fakenews.server.domain.auth.User;
import com.fakenews.server.domain.auth.UserRepository;
import com.fakenews.server.domain.post.repository.PostRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
class PostCreationTests {
    @Autowired MockMvc mvc;
    @Autowired UserRepository users;
    @Autowired PostRepository posts;
    private User author;

    @BeforeEach
    void setUp() {
        author = users.save(new User("writer@example.com", "unused", "작성자"));
    }

    @Test
    void createsAndReadsPostWithAuthenticatedAuthor() throws Exception {
        mvc.perform(post("/api/posts").with(user(author.getEmail()))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"content\":\"첫 게시글\\n본문입니다.\",\"userId\":999,\"isInitial\":true}"))
                .andExpect(status().isCreated()).andExpect(jsonPath("$.postId").isNumber());
        var saved = posts.findAll().get(0);
        assertThat(saved.getUserId()).isEqualTo(author.getId());
        assertThat(saved.getContent()).isEqualTo("첫 게시글\n본문입니다.");
        assertThat(saved.getIsInitial()).isFalse();
        assertThat(saved.getDeleted()).isFalse();
        assertThat(saved.getCreatedAt()).isNotNull();
        mvc.perform(get("/api/posts/" + saved.getPostId()).with(user(author.getEmail())))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content").value(saved.getContent()));
    }

    @Test
    void rejectsInvalidContentWithoutSaving() throws Exception {
        for (String body : new String[]{"{}", "{\"content\":null}", "{\"content\":\"\"}",
                "{\"content\":\"   \\n\"}", "{\"content\":\"" + "a".repeat(10001) + "\"}"}) {
            mvc.perform(post("/api/posts").with(user(author.getEmail()))
                            .contentType(MediaType.APPLICATION_JSON).content(body))
                    .andExpect(status().isBadRequest());
        }
        assertThat(posts.count()).isZero();
    }

    @Test
    void acceptsMaximumLengthOnLegacyRoute() throws Exception {
        mvc.perform(post("/post/register").with(user(author.getEmail()))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"content\":\"" + "a".repeat(10000) + "\"}"))
                .andExpect(status().isCreated());
        assertThat(posts.findAll().get(0).getContent()).hasSize(10000);
    }

    @Test
    void requiresAuthenticationAndExistingUser() throws Exception {
        mvc.perform(post("/api/posts").contentType(MediaType.APPLICATION_JSON)
                        .content("{\"content\":\"본문\"}"))
                .andExpect(status().isUnauthorized());
        mvc.perform(post("/api/posts").with(user("missing@example.com"))
                        .contentType(MediaType.APPLICATION_JSON).content("{\"content\":\"본문\"}"))
                .andExpect(status().isUnauthorized());
        assertThat(posts.count()).isZero();
    }

    @Test
    void missingPostReturnsNotFound() throws Exception {
        mvc.perform(get("/api/posts/999999").with(user(author.getEmail())))
                .andExpect(status().isNotFound());
    }
}
